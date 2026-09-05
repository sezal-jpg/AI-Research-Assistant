from app.core.logger import logger
from app.core.app_state import state

class ContextBuilderService:
    def build_context(self,ranked_docs,top_k=3):
        context=""
        top_docs=[]
        used_parents=set()
        
        for doc,score in ranked_docs:
            if len(top_docs)>=top_k:
                break
            
            parent_id=doc.metadata.get('parent_id')
            
            # Hierarchial RAG
            
            if parent_id and parent_id in state.parent_chunks:
                parent_doc=state.parent_chunks[parent_id]
                if parent_id in used_parents:
                    continue
                
                top_docs.append(parent_doc)
                used_parents.add(parent_id)
        
            else:
                top_docs.append(doc)
                
        for doc in top_docs:
            source=doc.metadata.get('source_file',doc.metadata.get('source_url','Unknown source'))
            page=doc.metadata.get('page',0)
            if isinstance(page,int):
                page+=1
                
            context+=f"""
            source: {source}
            page: {page}
            content: {doc.page_content}
            ------------------------
            """
        logger.info(f'build hierarchial context using {len(top_docs)} chunks')
        
        return context,top_docs  
 
context_builder_service=ContextBuilderService()     
            
            
    