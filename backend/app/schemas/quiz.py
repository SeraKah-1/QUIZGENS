from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# Schema untuk Response Status (Polling)
class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: datetime
    data: Optional[Any] = None # Hasil Quiz (JSON) kalau sudah completed
    error: Optional[str] = None

# Schema untuk Response Upload Awal
class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str