from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router # Import router baru

app = FastAPI(title="QuizGen AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pasang Router V1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "QuizGen API is Online 🚀"}