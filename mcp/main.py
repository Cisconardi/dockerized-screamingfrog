from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mcp.models import CrawlRequest
from mcp.runner import run_crawl
import uuid
import os
import subprocess

app = FastAPI()
crawl_states = {}

@app.post("/crawl")
def crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    crawl_id = str(uuid.uuid4())
    output_path = f"/output/{crawl_id}"
    os.makedirs(output_path, exist_ok=True)
    os.chmod(output_path, 0o777)  # Garantisce i permessi di scrittura
    req.output_folder = output_path
    crawl_states[crawl_id] = "running"
    background_tasks.add_task(run_and_capture, req, crawl_id)
    return {"status": "started", "crawl_id": crawl_id}

def run_and_capture(req: CrawlRequest, crawl_id: str):
    output_path = req.output_folder
    try:
        result = run_crawl(req)
        crawl_states[crawl_id] = "success"
    except Exception as e:
        result = None
        crawl_states[crawl_id] = f"failed: {str(e)}"
    finally:
        debug_path = os.path.join(output_path, "debug.log")
        with open(debug_path, "w") as f:
            f.write(f"Crawl ID: {crawl_id}\n")
            f.write(f"Status: {crawl_states[crawl_id]}\n")
            f.write(f"Output path: {output_path}\n")
            if result:
                f.write(f"Command: {result.get('command', '')}\n")
                f.write(f"Return code: {result.get('returncode', '')}\n")
                f.write(f"STDOUT:\n{result.get('stdout', '')}\n")
                f.write(f"STDERR:\n{result.get('stderr', '')}\n")
            if not os.path.exists(os.path.join(output_path, "internal_all.csv")):
                f.write("File internal_all.csv NOT FOUND\n")
            else:
                f.write("File internal_all.csv FOUND\n")

@app.get("/status/{crawl_id}")
def get_status(crawl_id: str):
    status = crawl_states.get(crawl_id)
    if not status:
        raise HTTPException(status_code=404, detail="Crawl ID not found")
    return {"crawl_id": crawl_id, "status": status}

@app.get("/download/{crawl_id}")
def download_report(crawl_id: str):
    filename = "internal_all.csv"
    path = f"/output/{crawl_id}/{filename}"
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, filename=f"{crawl_id}_{filename}", media_type="application/octet-stream")

app.mount("/static", StaticFiles(directory="/output"), name="static")
