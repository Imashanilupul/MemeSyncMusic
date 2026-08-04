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

    filepath = None

    youtube_audio_path = os.path.join(UPLOAD_FOLDER, job_id, "audio.mp3")
    if os.path.isfile(youtube_audio_path):
        filepath = youtube_audio_path
    else:
        files = os.listdir(UPLOAD_FOLDER)
        for file in files:
            candidate_path = os.path.join(UPLOAD_FOLDER, file)
            if file.startswith(job_id) and os.path.isfile(candidate_path):
                filepath = candidate_path
                break

    if filepath is None:
        raise HTTPException(status_code=404, detail="Audio not found")

    result = analyzer.analyze(filepath)

    with open(os.path.join(ANALYSIS_FOLDER, f"{job_id}.json"), "w") as f:

        json.dump(result, f, indent=4)

    return result
