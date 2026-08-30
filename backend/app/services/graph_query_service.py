from app.core.logger import logger
from app.services.graph_service import graph_service

class GraphQueryService:
    
    def search(self,query):
        logger.info(f'Graph search query: {query}')
        results=graph_service.search(query)
        logger.info(f'Graph search returned'
                f" {len(results)} relationships")
        
        return results
    
    def build_graph_context(self,query):
        results=self.search(query)
        if not results:
            return ""
        
        lines=[]
        for edge in results:
           lines.append(f"{edge['source']}"
                        f"--[{edge['relationship']}]-->"
                        f"{edge['target']}")
           
        return "\n".join(lines)   
    
graph_query_service=GraphQueryService()    