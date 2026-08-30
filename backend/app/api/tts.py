from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.services.tts_service import tts_service

router=APIRouter(prefix="",tags=['Text to speech'])
OUTPUT_DIR=Path('generated_audio')
OUTPUT_DIR.mkdir(exist_ok=True)

@router.post('/tts')
def generate_speech(request: dict):
    text=request.get('text',"").strip()
    
    if not text:
        return {'error:'"Text is required"}
    
    output_path=(OUTPUT_DIR/'answer.wav')
    result=tts_service.speak_to_file(text,str(output_path))
    
    if result is None:
        return{'error':'TTS generation failed'}
    return FileResponse(result,media_type='audio/wav',filename='answer.wav')