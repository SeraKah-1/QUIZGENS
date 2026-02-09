from fastapi import APIRouter
from app.api.v1 import endpoints

api_router = APIRouter()

# Masukkan endpoint quiz ke dalam router utama
api_router.include_router(endpoints.router, prefix="/quiz", tags=["Quiz"])