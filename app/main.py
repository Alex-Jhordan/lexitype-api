import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import WordRequest, WordResponse
from app.services import call_gemini_api, sanitize_topic

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate-words", response_model=WordResponse)
async def generate_words(payload: WordRequest) -> WordResponse:
    normalized_topic = sanitize_topic(payload.topic)

    try:
        return await call_gemini_api(normalized_topic)
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
