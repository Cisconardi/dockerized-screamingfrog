import logging
import os
import uuid
# subprocess is used by mcp.runner
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mcp.models import CrawlRequest
from mcp.runner import run_crawl

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
# In-memory storage for crawl states. Note: Data will be lost on application restart.
# For persistent storage, consider a database or file-based solution.
crawl_states = {}

# Updated crawl function
@app.post("/crawl")
def crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received new crawl request for URL: {req.url if req.url else 'list crawl'}")
    crawl_id = str(uuid.uuid4())
    output_path = f"/output/{crawl_id}"

    try:
        os.makedirs(output_path, exist_ok=True)
        os.chmod(output_path, 0o777)  # Setting permissive rights for output folder, common in Docker setups.
        logger.info(f"Output path {output_path} created and permissions set for crawl_id: {crawl_id}")
    except Exception as e:
        logger.error(f"Error creating output directory {output_path} for crawl_id: {crawl_id}. Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create output directory.")

    req.output_folder = output_path
    crawl_states[crawl_id] = "running"

    background_tasks.add_task(run_and_capture, req, crawl_id)
    logger.info(f"Crawl {crawl_id} started in background for URL: {req.url if req.url else 'list crawl'}")
    return {"status": "started", "crawl_id": crawl_id}

# Updated run_and_capture function
def run_and_capture(req: CrawlRequest, crawl_id: str):
    output_path = req.output_folder
    logger.info(f"Background task started for crawl ID: {crawl_id}, output path: {output_path}")
    try:
        result = run_crawl(req) # Expects dict: {command, stdout, stderr, returncode, output_folder}

        if result and result.get("returncode") == 0:
            crawl_states[crawl_id] = "success"
            logger.info(f"Crawl ID: {crawl_id} completed successfully.")
            logger.info(f"Crawl ID: {crawl_id} - Command: {result.get('command', 'N/A')}")
            logger.info(f"Crawl ID: {crawl_id} - Return code: {result.get('returncode', 'N/A')}")
            # Using triple quotes for potentially multi-line output
            logger.debug(f"Crawl ID: {crawl_id} - STDOUT:\n{result.get('stdout', 'N/A')}")
            logger.debug(f"Crawl ID: {crawl_id} - STDERR:\n{result.get('stderr', 'N/A')}")

            expected_file = os.path.join(output_path, "internal_all.csv")
            if not os.path.exists(expected_file):
                logger.warning(f"Crawl ID: {crawl_id} - File internal_all.csv NOT FOUND in {output_path} after successful crawl.")
            else:
                logger.info(f"Crawl ID: {crawl_id} - File internal_all.csv FOUND in {output_path}.")
        else:
            error_message = result.get('stderr', 'No stderr output.') if result else 'Screaming Frog execution did not return a result object.'
            return_code = result.get('returncode', 'N/A') if result else 'N/A'
            # Update state with more specific failure info
            crawl_states[crawl_id] = f"failed: Screaming Frog error. RC: {return_code}"
            logger.error(f"Crawl ID: {crawl_id} failed during Screaming Frog execution. Return code: {return_code}.")
            if result:
                logger.error(f"Crawl ID: {crawl_id} - Command: {result.get('command', 'N/A')}")
                logger.debug(f"Crawl ID: {crawl_id} - STDOUT:\n{result.get('stdout', 'N/A')}") # Log stdout even on failure for debugging
                logger.error(f"Crawl ID: {crawl_id} - STDERR:\n{error_message}") # Log actual stderr
            else: # This means 'result' itself is None or evaluates to False
                crawl_states[crawl_id] = "failed: Screaming Frog execution did not return result object." # More specific state
                logger.error(f"Crawl ID: {crawl_id} - run_crawl did not return a result object (it was None or empty).")

    except Exception as e:
        # Ensure consistent status format for "failed:"
        crawl_states[crawl_id] = f"failed: Unexpected exception: {str(e)}"
        logger.error(f"Crawl ID: {crawl_id} failed with an unexpected exception in run_and_capture. Exception: {str(e)}", exc_info=True)
    finally:
        final_status = crawl_states.get(crawl_id, "unknown")
        logger.info(f"Background task finished for crawl ID: {crawl_id}. Final state: {final_status}")

# get_status function (unchanged)
@app.get("/status/{crawl_id}")
def get_status(crawl_id: str):
    status = crawl_states.get(crawl_id)
    if not status:
        # No logger here as this is a simple status check, HTTPException is enough
        raise HTTPException(status_code=404, detail="Crawl ID not found")
    return {"crawl_id": crawl_id, "status": status}

# Updated download_report function
@app.get("/download/{crawl_id}")
def download_report(crawl_id: str):
    logger.info(f"Download attempt for crawl_id: {crawl_id}")
    status = crawl_states.get(crawl_id)

    if not status:
        logger.warning(f"Download failed: Crawl ID {crawl_id} not found.")
        raise HTTPException(status_code=404, detail=f"Crawl ID {crawl_id} not found.")

    logger.info(f"Crawl ID: {crawl_id}, Status from state: {status}")

    if status == "running":
        logger.info(f"Download denied: Crawl {crawl_id} is still in progress.")
        raise HTTPException(status_code=409, detail=f"Crawl {crawl_id} is still in progress. Please try again later.")
    elif status.startswith("failed"):
        logger.warning(f"Download failed: Crawl {crawl_id} previously failed. Error details: {status}")
        raise HTTPException(status_code=500, detail=f"Crawl {crawl_id} failed. No report available. Error: {status}")
    elif status == "success":
        filename = "internal_all.csv"
        path = f"/output/{crawl_id}/{filename}"
        if not os.path.isfile(path):
            logger.warning(f"Download failed: Report file {filename} not found for successful crawl {crawl_id} at path {path}.")
            raise HTTPException(status_code=404, detail=f"Report file {filename} not found for successful crawl {crawl_id}. The crawl completed, but the expected output file is missing.")
        logger.info(f"Successfully serving file {filename} for crawl_id {crawl_id} from path {path}.")
        return FileResponse(path, filename=f"{crawl_id}_{filename}", media_type="application/octet-stream")
    else:
        logger.error(f"Download failed: Crawl {crawl_id} is in an unknown state: {status}.")
        raise HTTPException(status_code=500, detail=f"Crawl {crawl_id} is in an unknown state: {status}.")

app.mount("/static", StaticFiles(directory="/output"), name="static")
