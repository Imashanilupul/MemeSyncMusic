from fastapi import APIRouter
from pydantic import BaseModel

from app.services.meme_service import MemeService

router = APIRouter(prefix="/meme", tags=["Meme"])


service = MemeService()


class MemeRequest(BaseModel):

    lyrics: str


@router.post("/search")
def search_meme(request: MemeRequest):

    return service.search(request.lyrics)
