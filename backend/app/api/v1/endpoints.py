from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from app.core.database import supabase
from app.services.hashing import calculate_hash
from app.services.pdf import extract_text_from_pdf
from app.services.llm import generate_quiz_content
import uuid
import json

router = APIRouter()

# --- BACKGROUND TASK ---
# Fungsi ini jalan di belakang layar setelah response dikirim ke user
def process_quiz_task(job_id: str, file_content: bytes, amount: int, difficulty: str):
    try:
        # 1. Update status jadi PROCESSING
        supabase.table("quiz_generations").update({"status": "processing"}).eq("id", job_id).execute()
        
        # 2. Extract PDF
        text = extract_text_from_pdf(file_content)
        
        # 3. Generate Quiz via Gemini
        quiz_json = generate_quiz_content(text, amount, difficulty)
        
        # 4. Simpan Hasil & Update status COMPLETED
        supabase.table("quiz_generations").update({
            "status": "completed",
            "quiz_data": quiz_json
        }).eq("id", job_id).execute()
        
        print(f"✅ Job {job_id} Completed!")

    except Exception as e:
        print(f"❌ Job {job_id} Failed: {e}")
        # Update status FAILED biar frontend tau
        supabase.table("quiz_generations").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", job_id).execute()

# --- ENDPOINTS ---

@router.post("/generate", response_model=dict)
async def generate_quiz(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    amount: int = Form(5),
    difficulty: str = Form("medium")
):
    # 1. Baca File
    content = await file.read()
    
    # 2. Cek Cache (Hash)
    metadata = {"amount": amount, "difficulty": difficulty}
    file_hash = calculate_hash(content, metadata)
    
    # Query ke DB: Adakah hash ini yang statusnya 'completed'?
    existing_job = supabase.table("quiz_generations").select("*")\
        .eq("file_hash", file_hash)\
        .eq("status", "completed")\
        .execute()
        
    if existing_job.data:
        # CACHE HIT! Langsung return ID lama
        return {
            "job_id": existing_job.data[0]['id'],
            "status": "completed",
            "message": "Quiz found in cache!"
        }
    
    # 3. CACHE MISS! Buat Job Baru
    new_job_id = str(uuid.uuid4())
    
    # Insert entry awal ke DB (Status: Pending)
    data = {
        "id": new_job_id,
        "filename": file.filename,
        "file_hash": file_hash,
        "status": "pending"
    }
    supabase.table("quiz_generations").insert(data).execute()
    
    # 4. Lempar ke Background Task
    background_tasks.add_task(process_quiz_task, new_job_id, content, amount, difficulty)
    
    return {
        "job_id": new_job_id,
        "status": "pending",
        "message": "Processing started in background"
    }

@router.get("/status/{job_id}")
async def check_status(job_id: str):
    response = supabase.table("quiz_generations").select("*").eq("id", job_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Job ID not found")
        
    job = response.data[0]
    
    return {
        "job_id": job['id'],
        "status": job['status'],
        "created_at": job['created_at'],
        "data": job.get('quiz_data'),  # Akan null jika belum selesai
        "error": job.get('error_message')
    }