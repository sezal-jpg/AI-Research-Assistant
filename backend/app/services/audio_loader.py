from pathlib import Path
from langchain_core.documents import Document
from app.core.logger import logger
from app.services.whisper_service import whisper_service
from app.services.content_safety_service import content_safety_service

class AudioLoader:
    def load(self,file_path:Path):
        logger.info(f'Loading Audio:{file_path.name}')
        
        transcript=whisper_service.transcribe(str(file_path))
        if not transcript.strip():
            logger.warning(f"No transcript generated for {file_path.name}")
            return []
        
        logger.info(
            f"Running text content safety check "
            f"for audio: {file_path.name}" )

        safety_result = (
            content_safety_service.check_text(
                transcript
            ) )

        if not safety_result["safe"]:
            if safety_result.get('error'):
                logger.error(f"Audio transcript safety analysis "
            f"failed: {file_path.name}: "
            f"{safety_result['error']}")
                
                raise ValueError(  "Audio could not be fully processed "
            "because its transcript could not be "
            "analyzed for content safety." )

            logger.warning(
                f"Unsafe audio transcript blocked: "
                f"{file_path.name}" )

            raise ValueError(
                "Upload blocked because the audio "
                "transcript was detected as sexually "
                "explicit or otherwise unsafe."
            )

        logger.info(
            f"Audio transcript safety check passed: "
            f"{file_path.name}" )
        
        docs=[Document(page_content=transcript,metadata={'source_file':file_path.name,'source_type':'audio'})]
        
        logger.info(f'Audio processed successfully:' f'{file_path.name}')
        
        return docs
    
audio_loader=AudioLoader()    