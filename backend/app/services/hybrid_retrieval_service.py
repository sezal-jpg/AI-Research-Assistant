from app.core.logger import logger
from app.services.retrieval_service import (retrieval_service)
from app.services.graph_retrieval_service import (graph_retrieval_service)

class HybridRetrievalService:
    def retrieve(self,question,selected_file='All Files'):
        logger.info('Hybrid retrieval started')
        
        rag_docs=retrieval_service.retrieval(question,selected_file)
        logger.info(f'Traditional RAG returned'
             f"{len(rag_docs)} documents")
        
        graph_results=(graph_retrieval_service.retrieve(question))
        logger.info(f'Graph retrieval returned' 
             f"{len(graph_results)} relationships")
        
        return {'documents':rag_docs,
                'graph_results':graph_results}
        
hybrid_retrieval_service=(HybridRetrievalService())        