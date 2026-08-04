from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video"])
service = VideoService()


class RenderVideoRequest(BaseModel):
    job_id: str
    slides: list[dict]
    source: str = "youtube"
    audio_file: str | None = None


@router.post("/render")
def render_video(request: RenderVideoRequest):
    try:
        output_path = service.render(
            job_id=request.job_id,
            slides=request.slides,
            source=request.source,
            audio_file=request.audio_file,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "success": True,
        "video_path": output_path,
        "video_url": f"/uploads/{request.job_id}/combined.mp4",
    }
