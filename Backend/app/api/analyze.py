import os
import json

from fastapi import APIRouter, HTTPException

from app.services.audio_analysis import AudioAnalyzer

router = APIRouter()

UPLOAD_FOLDER = "uploads"

ANALYSIS_FOLDER = "analysis"

os.makedirs(ANALYSIS_FOLDER, exist_ok=True)

analyzer = AudioAnalyzer()


@router.get("/analyze/{job_id}")
def analyze_audio(job_id: str):

    files = os.listdir(UPLOAD_FOLDER)

    target = None

    for file in files:

        if file.startswith(job_id):

            target = file

            break

    if target is None:

        raise HTTPException(status_code=404, detail="Audio not found")

    filepath = os.path.join(UPLOAD_FOLDER, target)

    result = analyzer.analyze(filepath)

    with open(os.path.join(ANALYSIS_FOLDER, f"{job_id}.json"), "w") as f:

        json.dump(result, f, indent=4)

    return result
