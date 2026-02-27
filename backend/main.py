from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil

from backend.core.downloader import download_video
from backend.core.extractor import extract_unique_frames
from backend.core.pdf_generator import create_pdf_from_frames

app = FastAPI(title="LectureFrame API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

# In-memory store for task status 
# Format: { "task_id": {"status": "processing" | "completed" | "error", "pdf_path": "", "message": ""} }
tasks_store = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

def process_video_task(task_id: str, url: str):
    task_dir = os.path.join(TMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    frames_dir = os.path.join(task_dir, "frames")
    
    try:
        tasks_store[task_id] = {"status": "downloading", "message": "Downloading video"}
        video_path = download_video(url, task_dir)
        
        tasks_store[task_id] = {"status": "extracting", "message": "Extracting unique frames"}
        frames = extract_unique_frames(video_path, frames_dir, threshold=0.85, sampling_rate=1)
        
        tasks_store[task_id] = {"status": "generating", "message": "Generating PDF slides"}
        pdf_path = os.path.join(task_dir, f"{task_id}.pdf")
        
        if not frames:
            raise Exception("No unique frames could be extracted from the video.")
            
        create_pdf_from_frames(frames, pdf_path)
        
        # Cleanup video and frames to save space
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
            
        tasks_store[task_id] = {
            "status": "completed", 
            "message": "PDF ready", 
            "pdf_path": pdf_path
        }
    except Exception as e:
        tasks_store[task_id] = {"status": "error", "message": str(e)}

@app.post("/api/process")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks_store[task_id] = {"status": "queued", "message": "Task queued"}
    background_tasks.add_task(process_video_task, task_id, request.url)
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    return {
        "task_id": task_id,
        "status": task.get("status"),
        "message": task.get("message")
    }

@app.get("/api/download/{task_id}")
async def download_pdf(task_id: str):
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task = tasks_store[task_id]
    if task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="PDF is not ready yet")
        
    pdf_path = task.get("pdf_path")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
        
    return FileResponse(
        pdf_path, 
        media_type="application/pdf", 
        filename="LectureFrame_Slides.pdf"
    )

@app.get("/")
def read_root():
    return {"message": "LectureFrame API is running"}
