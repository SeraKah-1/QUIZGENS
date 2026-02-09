import hashlib
import json

def calculate_hash(file_content: bytes, metadata: dict) -> str:
    """
    Membuat SHA256 hash dari konten file + metadata request.
    Ini memastikan cache unik berdasarkan file DAN setting quiz.
    """
    hasher = hashlib.sha256()
    
    # 1. Masukkan konten file
    hasher.update(file_content)
    
    # 2. Masukkan metadata (diurutkan key-nya biar konsisten)
    # Contoh metadata: {"amount": 10, "difficulty": "hard"}
    metadata_str = json.dumps(metadata, sort_keys=True)
    hasher.update(metadata_str.encode('utf-8'))
    
    return hasher.hexdigest()