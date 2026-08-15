from typing import List
from pathlib import Path
from fastapi import UploadFile
from app.core.logger import logger
from app.services.indexing_service import indexing_service
from app.services.loader_factory import loader_factory

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
        saved_files=await self.save_uploaded_files(files)
        all_docs=[]
        
        for file_path in saved_files:
            logger.info(f'Processing {file_path.name}')
            
            loader=loader_factory.get_loader(file_path)
            if loader is None:
                logger.warning(f'Unsupported file: {file_path.name}')
                continue
            docs=loader.load(file_path)
            
            docs=self.add_metadata(docs,file_path.name,)
            all_docs.extend(docs)
            
        chunks=indexing_service.index_documents(all_docs)
        
        logger.info(f'total documents : {len(all_docs)}')
        logger.info(f'total chunks :{len(chunks)}')

        
        return {
            'message':'Documents indexed successfully',
            'uploaded_files':len(saved_files),
            'documents':len(all_docs),
            'chunks':len(chunks),
            
        }
            
        
    def add_metadata(self,docs,filename):
        for doc in docs:
            doc.metadata['source_file']=filename
        return docs        
                
ingestion_service = IngestionService()