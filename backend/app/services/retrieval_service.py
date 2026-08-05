from app.core.app_state import state
from app.core.logger import logger
from langchain_community.retrievers import BM25Retriever
class RetrievalService:
    
    def retrieval(self,question:str,selected_file:str):
        if state.vectorstore is None or state.bm25_retriever is None:
            return [],[]
        logger.info('Running semantic search')
        
        if selected_file=='All PDFs':
            semantic_docs=state.vectorstore.similarity_search(question,k=3)
            bm25_docs=state.bm25_retriever.invoke(question)
            
        else:
            semantic_docs=state.vectorstore.similarity_search(question,k=8,filter={'source_file':selected_file})  
            filtered_chunks=[chunk for chunk in state.all_chunks
                             if chunk.metadata['source_file']==selected_file]
            filtered_bm25=BM25Retriever.from_documents(filtered_chunks)  
            filtered_bm25.k=8
            bm25_docs=filtered_bm25.invoke(question)
            
        docs=semantic_docs+bm25_docs
        unique_docs=[]
        seen=set()
        
        for doc in docs:
            if doc.page_content not in seen:
                unique_docs.append(doc)
                seen.add(doc.page_content)
        logger.info(f'Retrieved {len(unique_docs)} unique chunks')
        
        return unique_docs      
    
retrieval_service=RetrievalService()        