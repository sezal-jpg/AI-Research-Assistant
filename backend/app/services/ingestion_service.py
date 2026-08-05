from typing import List
from pathlib import Path
from fastapi import UploadFile
from app.core.logger import logger
from app.core.app_state import state
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.embedding_service import get_embedding_model
from app.services.document_loader import document_loader
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
embedding_model=get_embedding_model()

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
            logger.info(f'Loading {file_path.name}')
            docs=document_loader.load(file_path)
            docs=self.add_metadata(docs,file_path.name)
            all_docs.extend(docs)
            
        splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50,) 
        chunks=splitter.split_documents(all_docs)
        logger.info(f'created {len(chunks)} chunks')
        state.all_chunks=chunks  
        
        state.vectorstore=Chroma.from_documents(documents=chunks,embedding=embedding_model,persist_directory='db')
         
        state.bm25_retriever=BM25Retriever.from_documents(chunks)
        state.bm25_retriever.k=3
        
        logger.info(f'total documents : {len(all_docs)}')
        logger.info(f'total chunks :{len(chunks)}')
        logger.info(f'vector DB created :{state.vectorstore is not None}')
        logger.info(f"BM25 Created : {state.bm25_retriever is not None}")
        
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