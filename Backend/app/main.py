from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.uploadMusic import router as Music_Uploader

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


@app.get("/")
def home():
    return {"message": "MemeSync API Running"}
