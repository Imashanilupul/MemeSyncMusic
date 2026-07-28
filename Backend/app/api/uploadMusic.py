import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

ALLOWED = [".mp3", ".wav"]

UPLOAD_FOLDER = "uploads"


@router.post("/upload")
async def upload_music(file: UploadFile = File(...)):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED:
        raise HTTPException(
            status_code=400, detail="Only MP3 and WAV files are allowed."
        )

    job_id = str(uuid.uuid4())

    filename = f"{job_id}{extension}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"success": True, "job_id": job_id, "filename": filename}
