from faster_whisper import WhisperModel
from app.core.logger import logger

class WhisperService:
    
    def __init__(self):
        
        logger.info('Loading Whisper model...')
        self.model=WhisperModel('base',device='cpu',compute_type='int8')
        
    def transcribe(self,audio_path:str):
        logger.info(f'Transcribing audio:{audio_path}')
        try:
            segments,info=self.model.transcribe(audio_path,beam_size=5)
            transcript=[]
            for segment in segments:
                transcript.append(segment.text.strip())    
             
            text=" ".join(transcript).strip()  
            logger.info(f"Transcription completed:"f"{len(text)} characters")
            
            return text
        
        except Exception as e:
            logger.error(f'Whisper transcription failed: {e}')  
            
            return ""
        
whisper_service=WhisperService()        