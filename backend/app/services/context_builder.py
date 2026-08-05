from app.core.logger import logger

class ContextBuilderService:
    def build_context(self,ranked_docs,top_k=3):
        context=""
        top_docs=[doc for doc, score in ranked_docs[:top_k]]
        
        for doc in top_docs:
            source=doc.metadata.get('source_file','Unknown PDF')
            page=doc.metadata.get('page',0)+1
            context+=f"""
            source: {source}
            page: {page}
            content: {doc.page_content}
            ------------------------
            """
        logger.info(f'build context using {len(top_docs)} chunks')
        
        return context,top_docs  
 
context_builder_service=ContextBuilderService()     
            
            
    