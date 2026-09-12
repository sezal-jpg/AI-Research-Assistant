from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ingestion_service import ingestion_service

router=APIRouter(prefix='/youtube',tags=['YouTube'])
class YouTubeRequest(BaseModel):
    url:str
    
class YouTubeTranscriptRequest(BaseModel):
    url:str
    transcript:str    
    
@router.post('/upload')
async def upload_youtube(request:YouTubeRequest) :
    result=(await ingestion_service.process_youtube(request.url))
    return result

@router.post('/upload-transcript')
async def upload_youtube_transcript(request: YouTubeTranscriptRequest):
    result=await ingestion_service.process_youtube_transcript(request.url,request.transcript)
    return result
