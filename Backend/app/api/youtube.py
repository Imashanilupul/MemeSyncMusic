from fastapi import APIRouter
from pydantic import BaseModel

from app.services.youtube_service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube"])

service = YouTubeService()


class YoutubeRequest(BaseModel):
    url: str


@router.post("/transcript")
def transcript(data: YoutubeRequest):

    return service.get_transcript(data.url)
