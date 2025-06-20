from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from mcp.runner import run_crawl
import uuid
import os

app = FastAPI()
crawl_states = {}

class CrawlRequest(BaseModel):
    url: str
    export_tabs: list[str] = ["Internal:All"]
    export_format: str = "csv"
    output_folder: str | None = None

@app.post("/crawl")
def crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    crawl_id = str(uuid.uuid4())
    output_path = f"/output/{crawl_id}"
    os.makedirs(output_path, exist_ok=True)
    crawl_states[crawl_id] = "running"
    background_tasks.add_task(run_and_capture, req, output_path, crawl_id)
    return {"status": "started", "crawl_id": crawl_id}

def run_and_capture(req: CrawlRequest, output_path: str, crawl_id: str):
    try:
        req.output_folder = output_path  # imposta dinamicamente la cartella
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

@app.get("/download/{crawl_id}")
def download_report(crawl_id: str):
    filename = "Internal_All.csv"
    path = f"/output/{crawl_id}/{filename}"
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, filename=f"{crawl_id}_{filename}", media_type="application/octet-stream")
