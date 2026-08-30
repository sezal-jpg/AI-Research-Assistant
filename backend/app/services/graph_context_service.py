from app.core.logger import logger

class GraphContextService:
    
    def build_context(self,graph_results):
        if not graph_results:
            return ""
        context="\nGRAPH RELATIONSHIPS:\n"
        
        for edge in graph_results:
            source=edge.get('source','Unknown')
            relationship=edge.get('relationship','related_to')
            target=edge.get('target','Unknown')
            
            context+=(f'{source}'
                      f"-[{relationship}]->"
                      f"{target}\n")
            
            logger.info(f'Built graph context using'
                        f"{len(graph_results)} relationships")
            
            return context
        
graph_context_service=(GraphContextService())        
        