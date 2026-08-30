from pathlib import Path
from langchain_core.documents import Document
from app.core.logger import logger
from app.services.whisper_service import whisper_service

class AudioLoader:
    def load(self,file_path:Path):
        logger.info(f'Loading Audio:{file_path.name}')
        
        transcript=whisper_service.transcribe(str(file_path))
        if not transcript.strip():
            logger.warning(f'No transcript generated for'f"{file_path.name}")
            return []
        docs=[Document(page_content=transcript,metadata={'source_file':file_path.name,'source_type':'audio'})]
        
        logger.info(f'Audio processed successfully:' f'{file_path.name}')
        
        return docs
    
audio_loader=AudioLoader()    