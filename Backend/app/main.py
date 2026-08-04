from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.uploadMusic import router as Music_Uploader
from app.api.analyze import router as analyze_router

# from app.api.transcription import router as transcription_router
from app.api.youtube import router as youtube_router
from app.api.meme import router as meme_extractor
from app.api.video import router as video_router

app = FastAPI(title="MemeSyncMusic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs("uploads", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(Music_Uploader)
app.include_router(analyze_router)
# app.include_router(transcription_router)
app.include_router(youtube_router)
app.include_router(meme_extractor)
app.include_router(video_router)


@app.get("/")
def home():
    return {"message": "MemeSync API Running"}
