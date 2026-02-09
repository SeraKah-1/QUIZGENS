import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
import io
import asyncio
import json
import uuid

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Memory
jobs = {}

# --- MODEL DATA ---
class TopicRequest(BaseModel):
    topic: str
    amount: int = 5

# --- FUNGSI AI (Digunakan kedua endpoint) ---
async def process_ai(job_id: str, prompt_content: str, amount: int):
    try:
        jobs[job_id]["status"] = "processing"
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Buatlah {amount} soal pilihan ganda dalam format JSON murni.
        Struktur: {{ "title": "Judul", "questions": [ {{ "question": "...", "options": ["A","B","C","D"], "answer_index": 0, "explanation": "..." }} ] }}
        
        Materi/Topik:
        {prompt_content[:15000]}
        """
        
        response = await model.generate_content_async(prompt)
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        jobs[job_id]["data"] = json.loads(cleaned)
        jobs[job_id]["status"] = "completed"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

# --- ENDPOINT 1: KHUSUS FILE (MULTIPART) ---
@app.post("/api/v1/quiz/upload")
async def upload_pdf(file: UploadFile = File(...), amount: int = Form(5)):
    job_id = str(uuid.uuid4())
    
    # Baca File
    content = ""
    if file.filename.endswith(".pdf"):
        pdf = PyPDF2.PdfReader(io.BytesIO(await file.read()))
        for p in pdf.pages: content += p.extract_text() + "\n"
    elif file.filename.endswith(".md") or file.filename.endswith(".txt"):
        content = (await file.read()).decode()
    else:
        raise HTTPException(400, "Format harus PDF/MD/TXT")
    
    jobs[job_id] = {"status": "queued"}
    asyncio.create_task(process_ai(job_id, content, amount))
    return {"job_id": job_id}

# --- ENDPOINT 2: KHUSUS TOPIK (JSON) ---
@app.post("/api/v1/quiz/topic")
async def create_from_topic(req: TopicRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued"}
    asyncio.create_task(process_ai(job_id, req.topic, req.amount))
    return {"job_id": job_id}

# --- STATUS CHECK ---
@app.get("/api/v1/quiz/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/")
def root(): return {"status": "ok"}