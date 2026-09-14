from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.whisper_service import whisper_service
from app.services.content_safety_service import content_safety_service
from app.core.logger import logger


router = APIRouter(
    prefix="",
    tags=["Audio"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)):

    audio_path = f"uploads/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    text = whisper_service.transcribe(
        audio_path
    )

    logger.info(
        f"Running text content safety check "
        f"for audio transcription: {file.filename}"
    )

    safety_result = (
        content_safety_service.check_text(
            text
        )
    )

    if not safety_result["safe"]:
        logger.warning(
            f"Unsafe audio transcription blocked: "
            f"{file.filename}"
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Audio transcription blocked because "
                "the detected content was sexually explicit "
                "or otherwise unsafe."
            )
        )

    logger.info(
        f"Audio transcription safety check passed: "
        f"{file.filename}"
    )

    return {
        "text": text
    }