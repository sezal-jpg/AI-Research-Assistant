from fastapi import APIRouter, HTTPException
from app.services.website_service import website_service
from app.models.Website import WebsiteRequest
from app.core.logger import logger

router = APIRouter(
    prefix="",
    tags=["Website"])

@router.post("/upload-website")
def upload_website(
    request: WebsiteRequest):

    try:
        return website_service.upload(
            request
        )

    except ValueError as e:

        logger.warning(
            f"Website upload blocked: {e}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )