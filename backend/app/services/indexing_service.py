from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from app.core.app_state import state
from app.core.logger import logger
from app.services.graph_construction_service import (graph_construction_service)
from langchain_community.vectorstores.utils import filter_complex_metadata
from app.services.embedding_service import get_embedding_model

class IndexingService:
    def __init__(self):
        self.embedding_model=get_embedding_model()
        self.parent_splitter=RecursiveCharacterTextSplitter(chunk_size=1500,chunk_overlap=150)
        
        self.child_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        
        
    def index_documents(self,docs):
        logger.info(f'Documents received for indexing: {len(docs)}')
        
        for index,doc in enumerate(docs[:3]):
            logger.info(f'Document{index}:'
                        f"characters={len(doc.page_content)},"
                        f"metadata={doc.metadata}")
            
        parent_chunks=self.parent_splitter.split_documents(docs)
        logger.info(f'created {len(parent_chunks)} parent chunks')
        chunks=[]
        
        for parent_index,parent in enumerate(parent_chunks):
            parent_id=f"{parent.metadata.get('source_file','unknown')}_{parent_index}"
            
            parent.metadata['parent_id']=parent_id
            parent.metadata['chunk_type']='parent'
            
            state.parent_chunks[parent_id]=parent
            
            child_chunks=self.child_splitter.split_documents([parent])
            
            for child_index ,child in enumerate(child_chunks):
                child.metadata['parent_id']=parent_id
                child.metadata['parent_index']=parent_index
                child.metadata['child_index']=child_index
                child.metadata['chunk_type']='child'
                
                chunks.append(child)
                
        logger.info(f'created {len(chunks)} chunks')  
        
        for parent in parent_chunks:
            try:
                graph_construction_service.build_from_document(parent)
                
            except Exception as e:
                logger.error(f'Graph construction failed: {e}')   
                
        if not chunks:
            logger.warning('No chunks were created.skipping indexing')
            return []
        
        if state.all_chunks is None:
            state.all_chunks=[]
        state.all_chunks.extend(chunks) 
        
        if chunks:
            logger.info(f'sample chunk metadata:{chunks[0].metadata}')
            
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