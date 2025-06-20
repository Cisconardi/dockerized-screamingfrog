from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from mcp.models import CrawlRequest
from mcp.runner import run_crawl
import uuid
import os

app = FastAPI()
crawl_states = {}

@app.post("/crawl")
def crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    crawl_id = str(uuid.uuid4())
    output_path = f"/output/{crawl_id}"
    os.makedirs(output_path, exist_ok=True)
    req.output_folder = output_path
    crawl_states[crawl_id] = "running"
    background_tasks.add_task(run_and_capture, req, crawl_id)
    return {"status": "started", "crawl_id": crawl_id}

def run_and_capture(req: CrawlRequest, crawl_id: str):
    try:
        run_crawl(req)
        crawl_states[crawl_id] = "success"
    except Exception as e:
        crawl_states[crawl_id] = f"failed: {str(e)}"

@app.get("/status/{crawl_id}")
def get_status(crawl_id: str):
    status = crawl_states.get(crawl_id)
    if not status:
        raise HTTPException(status_code=404, detail="Crawl ID not found")
    return {"crawl_id": crawl_id, "status": status}

# ROUTE DINAMICA PER DOWNLOAD
@app.get("/download/{crawl_id}")
def download_report(crawl_id: str):
    filename = "internal_all.csv"
    path = f"/output/{crawl_id}/{filename}"
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, filename=f"{crawl_id}_{filename}", media_type="application/octet-stream")

# MOUNT STATICO PER DEBUG
app.mount("/static", StaticFiles(directory="/output"), name="static")
