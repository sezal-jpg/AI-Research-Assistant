from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ingestion_service import ingestion_service

router=APIRouter(prefix='/youtube',tags=['YouTube'])
class YouTubeRequest(BaseModel):
    url:str
    
@router.post('/upload')
async def upload_youtube(request:YouTubeRequest) :
    result=(await ingestion_service.process_youtube(request.url))
    return result