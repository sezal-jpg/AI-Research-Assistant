from typing import List
from pathlib import Path
from fastapi import UploadFile
from app.core.logger import logger
from langchain_core.documents import Document
from app.services.indexing_service import indexing_service
from app.services.loader_factory import loader_factory
from app.services.youtube_service import youtube_service

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
            
    async def process_youtube(self,url:str):
        logger.info(f'Processing YouTube URL: {url}')   
        docs=(youtube_service.get_transcript(url))
        if not docs:
            logger.warning('No YouTube transcript found')  
            
            return {'message':'could not extract YouTube transcipt','documents':0,'chunks':0,} 
        
        chunks=(indexing_service.index_documents(docs))  
        logger.info(f'YouTube documents:' f'{len(chunks)}')
        logger.info(f'YouTube chunks:' f'{len(chunks)}')
        
        return {'message':'YouTube indexed successfully','documents':len(docs),'chunks':len(chunks),}
    
    async def process_youtube_transcript(self,url:str,transcript:str):
        logger.info(f'Processing youtube transcript: {url}')
        video_id=youtube_service.extract_video_id(url)
        
        if not video_id:
            logger.error('could not extract youtube video id')
            return {'message':'Invalid Youtube URL',
                    'documents':0,
                    'chunks':0}
            
        transcript=transcript.strip()
        if not transcript:
            logger.warning('Youtube transcript is empty')
            return{
                'message':'Youtube transcript is empty',
                'documents':0,
                'chunks':0
            }
            
        docs=[Document(page_content=transcript,metadata={
            'source_type':'youtube',
            'source_file':f'youtube:{video_id}',
            'source_url':url,
            'video_id':video_id,})]    
        
        chunks=indexing_service.index_documents(docs)
        logger.info(f'Youtube transcript documents" {len(docs)}')
        logger.info(f'Youtube transcript chunks: {len(chunks)}')
        
        return {
            'message':'Youtube indexed successfully',
            'documents':len(docs),
            'chunks':len(chunks)
        }
                    
    def add_metadata(self,docs,filename):
        for doc in docs:
            doc.metadata['source_file']=filename
        return docs        
                
ingestion_service = IngestionService()