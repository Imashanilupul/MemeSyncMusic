import json
import os

from fastapi import APIRouter, HTTPException

from app.services.transcription_service import TranscriptionService

router = APIRouter()

UPLOAD_FOLDER = "uploads"
TRANSCRIPT_FOLDER = "transcripts"

os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

service = TranscriptionService()


@router.get("/transcribe/{job_id}")
def transcribe(job_id: str):

    target = None

    for file in os.listdir(UPLOAD_FOLDER):

        if file.startswith(job_id):

            target = file

            break

    if target is None:

        raise HTTPException(status_code=404, detail="Audio not found")

    filepath = os.path.join(UPLOAD_FOLDER, target)

    result = service.transcribe(filepath)

    with open(
        os.path.join(TRANSCRIPT_FOLDER, f"{job_id}.json"), "w", encoding="utf8"
    ) as f:

        json.dump(result, f, indent=4, ensure_ascii=False)

    return result
