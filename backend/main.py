import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
import io
import asyncio
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# CORS: Izinkan semua akses (Penting buat Frontend kamu)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

async def process_quiz(job_id: str, content: str, amount: int, mode: str):
    try:
        jobs[job_id]["status"] = "processing"
        
        # Prompt Engineering sesuai Mode
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        base_prompt = f"""
        Buatlah {amount} soal pilihan ganda.
        Format output WAJIB JSON murni (list of objects) tanpa markdown ```json.
        Struktur JSON:
        {{
            "title": "Judul Kuis",
            "questions": [
                {{
                    "question": "Pertanyaan",
                    "options": ["A", "B", "C", "D"],
                    "answer_index": 0,  (0=A, 1=B, etc)
                    "explanation": "Penjelasan singkat"
                }}
            ]
        }}
        """

        if mode == "file":
            final_prompt = f"{base_prompt}\n\nBerdasarkan materi teks berikut:\n{content[:15000]}"
        else: # mode topic
            final_prompt = f"{base_prompt}\n\nTopik Kuis: {content}. Buat soal yang relevan, akurat, dan edukatif tentang topik tersebut."

        response = await model.generate_content_async(final_prompt)
        
        # Bersihkan hasil JSON dari Gemini
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        quiz_data = json.loads(cleaned_text)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["data"] = quiz_data

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"Error Job {job_id}: {e}")

@app.post("/api/v1/quiz/generate")
async def generate_quiz(
    file: UploadFile = File(None), # File jadi Optional
    topic: str = Form(None),       # Topic jadi Optional
    amount: int = Form(5),
    mode: str = Form("file")       # 'file' atau 'topic'
):
    import uuid
    job_id = str(uuid.uuid4())
    
    content = ""
    
    # Logic Pemrosesan Input
    try:
        if mode == "file":
            if not file:
                raise HTTPException(status_code=400, detail="File wajib diupload untuk mode file")
            
            file_content = await file.read()
            
            # Cek tipe file
            if file.filename.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            elif file.filename.endswith(".md") or file.filename.endswith(".txt"):
                content = file_content.decode("utf-8")
            else:
                raise HTTPException(status_code=400, detail="Format harus PDF atau MD")
                
        elif mode == "topic":
            if not topic:
                raise HTTPException(status_code=400, detail="Topik harus diisi")
            content = topic
            
    except Exception as e:
        return {"error": str(e)}

    jobs[job_id] = {"status": "queued", "data": None}
    
    # Jalankan background task
    asyncio.create_task(process_quiz(job_id, content, amount, mode))
    
    return {"job_id": job_id, "message": "Processing started"}

@app.get("/api/v1/quiz/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/")
def root():
    return {"message": "QuizGen Backend Ready"}