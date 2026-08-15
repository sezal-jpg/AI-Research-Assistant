from fastapi import APIRouter
from app.services.website_service import website_service
from app.models.Website import WebsiteRequest

router=APIRouter(prefix="",tags=['Website'])

@router.post("/upload-website")
def upload_website(request:WebsiteRequest):
    return website_service.upload(request)
