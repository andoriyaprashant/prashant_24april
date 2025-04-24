from fastapi import FastAPI
from fastapi.responses import FileResponse
from flask import send_from_directory
from . import report_generator
from fastapi import HTTPException
import os

app = FastAPI()
tasks = {}

@app.post("/trigger_report")
async def trigger_report():
    report_id = report_generator.start_report_generation()
    tasks[report_id] = "Running"
    return {"report_id": report_id}

@app.get("/get_report")
async def get_report(report_id: str):
    status = report_generator.get_report_status(report_id)
    if status == "Running":
        return {"status": "Running"}
    return {"status": "Complete", "download_url": f"/download/{report_id}"}


@app.get("/download/{report_id}")
async def download_report(report_id: str):
    report_file = os.path.join("reports", f"report_{report_id}.csv")
    
    if os.path.exists(report_file):
        return FileResponse(path=report_file, filename=f"report_{report_id}.csv", media_type='text/csv')
    else:
        raise HTTPException(status_code=404, detail="File not found")