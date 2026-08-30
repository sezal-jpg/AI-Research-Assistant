from app.core.logger import logger
from app.services.graph_service import graph_service

class GraphRetrievalService:
    
    def retrieve(self,question):
        logger.info(f'Graph enhanced retrieval started for :{question}')
        question_lower=question.lower()
        results=[]
        
        matched_nodes=[]
        for node_id in graph_service.nodes:
            if node_id.lower() in question_lower:
                matched_nodes.append(node_id)
                
        logger.info(f'Graph entities matched :{matched_nodes}')
        
        for edge in graph_service.edges:
            if(edge['source'] in matched_nodes or edge['target'] in matched_nodes):
                if edge not in results:
                    results.append(edge)
      
        logger.info(f'Graph retrieval returned'
                    f"{len(results)} relationships")
        
        return results
    
graph_retrieval_service=GraphRetrievalService()    