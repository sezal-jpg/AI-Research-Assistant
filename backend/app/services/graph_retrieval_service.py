from app.core.logger import logger
from app.services.graph_query_service import graph_query_service

class GraphRetrievalService:
    
    def retrieve(self,question):
        logger.info(f'Graph enhanced retrieval started for :{question}')
        results=graph_query_service.search(question)
      
        logger.info(f'Graph retrieval returned'
                    f"{len(results)} relationships")
        
        return results
    
graph_retrieval_service=GraphRetrievalService()    