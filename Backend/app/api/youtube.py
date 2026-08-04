from fastapi import APIRouter
from pydantic import BaseModel

from app.services.youtube_service import YouTubeService

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
)

service = YouTubeService()


class YoutubeRequest(BaseModel):
    url: str


@router.post("/process")
def process(request: YoutubeRequest):

    return service.process(request.url)
