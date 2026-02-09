import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz_content(text_source: str, amount: int = 5, difficulty: str = "medium"):
    """
    Kirim teks ke Gemini dan minta output JSON strik.
    """
    
    # Prompt Engineering (Sangat Spesifik)
    prompt = f"""
    Anda adalah asisten dosen ahli. Tugas anda membuat kuis pilihan ganda dari teks berikut.
    
    Konteks Materi:
    {text_source[:50000]}  # Batasi 50k karakter biar aman
    
    Instruksi:
    1. Buat {amount} soal pilihan ganda.
    2. Tingkat kesulitan: {difficulty}.
    3. Output HARUS valid JSON dengan struktur persis seperti ini:
    {{
        "title": "Judul Kuis yang Relevan",
        "questions": [
            {{
                "id": 1,
                "question": "Pertanyaan...",
                "options": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
                "answer_index": 0,  # Index array jawaban benar (0-3)
                "explanation": "Penjelasan kenapa jawaban itu benar."
            }}
        ]
    }}
    
    JANGAN gunakan markdown ```json```. Langsung raw JSON saja.
    Pastikan bahasa Indonesia baku.
    """

    try:
        # Gunakan Model Flash (Cepat & Murah) atau Pro (Pintar)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        
        # Parsing string JSON ke Python Dict
        quiz_data = json.loads(response.text)
        return quiz_data
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Return fallback error biar backend nggak crash
        return {"error": "Gagal generate kuis", "detail": str(e)}