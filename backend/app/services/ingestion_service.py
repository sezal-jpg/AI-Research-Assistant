from typing import List
from pathlib import Path
from fastapi import UploadFile
from app.core.logger import logger
from app.core.app_state import state
from app.core.logger import logger
from app.services.embedding_service import get_embedding_model
class IngestionService:
    def __init__(self):
        self.upload_dir=Path('uploads')
        self.upload_dir.mkdir(exist_ok=True)
    async def save_uploaded_files(
        self,files:List[UploadFile]
    ) ->List[Path]:
        saved_files=[]
        for file in files:
            file_path=self.upload_dir/file.filename
            logger.info(f'saving {file.filename}')
            with open(file_path,'wb') as f:
                f.write(await file.read())
            saved_files.append(file_path)
        return saved_files
    async def process_documents(self,files:List[UploadFile]):
        saved_files=await self.save_upload_files(files)
        return {
            'message':'Files saved successfully',
            'uploaded_files':len(saved_files),
            'files':[str(path) for path in saved_files]
            
        }
                
ingestion_service = IngestionService()