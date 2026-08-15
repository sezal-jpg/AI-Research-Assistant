from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from app.core.app_state import state
from app.core.logger import logger
from langchain_community.vectorstores.utils import filter_complex_metadata
from app.services.embedding_service import get_embedding_model

class IndexingService:
    def __init__(self):
        self.embedding_model=get_embedding_model()
        self.splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        
    def index_documents(self,docs):
        chunks=self.splitter.split_documents(docs)
        logger.info(f'created {len(chunks)} chunks')  
        if state.all_chunks is None:
            state.all_chunks=[]
        state.all_chunks.extend(chunks) 
        logger.info(f'Total Chunks in memory: {len(state.all_chunks)}')
        if state.vectorstore is None:
        
            state.vectorstore=Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory='db',
        ) 
        
            logger.info("Vector DB created successfully")
        else:
            state.vectorstore.add_documents(chunks)    
            logger.info('chunks added to existing vector db')
        
        state.bm25_retriever=BM25Retriever.from_documents(state.all_chunks)
        state.bm25_retriever.k=3
        
        logger.info("BM25 retriever created successfully")
        return chunks
    
indexing_service=IndexingService()    