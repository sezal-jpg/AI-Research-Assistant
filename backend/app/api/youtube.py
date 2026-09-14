from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ingestion_service import ingestion_service
from app.core.logger import logger

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"]
)


class YouTubeRequest(BaseModel):
    url: str

class YouTubeTranscriptRequest(BaseModel):
    url: str
    transcript: str


@router.post("/upload")
async def upload_youtube(
    request: YouTubeRequest
):

    try:

        result = await ingestion_service.process_youtube(
            request.url
        )
        return result

    except ValueError as e:

        logger.warning(
            f"YouTube upload blocked: {e}"
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/upload-transcript")
async def upload_youtube_transcript(
    request: YouTubeTranscriptRequest
):

    try:

        result = (
            await ingestion_service.process_youtube_transcript(
                request.url,
                request.transcript
            )
        )

        return result

    except ValueError as e:

        logger.warning(
            f"YouTube transcript blocked: {e}"
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )