from fastapi import APIRouter,UploadFile,File
from app.services.whisper_service import whisper_service

router=APIRouter(prefix="",tags=['Audio'])
@router.post('/transcribe')
async def transcribe_audio(file:UploadFile=File(...)):
    audio_path=(f'uploads/{file.filename}')
    with open(audio_path,'wb') as f:
        f.write(await file.read())
        
    text=whisper_service.transcribe(audio_path)
    
    return {'text':text}    
