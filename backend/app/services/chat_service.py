from app.core.logger import logger
from app.services.reranker_service import reranker_service
from app.services.retrieval_service import retrieval_service
from app.services.context_builder import context_builder_service
from app.services.generation_service import generation_service
from app.services.memory_service import memory_service
from app.services.source_service import source_service
from app.services.confidence_service import confidence_service

class ChatService:
    
    def ask(self,request):
        
        logger.info(f'Question received: {request.question}')
        
        docs=retrieval_service.retrieval(request.question,request.selected_pdf)
        if not docs:
            return {
                 "answer": "I couldn't find this information in the uploaded document(s).",
                "confidence": "Very Low",
                "sources": [],
                "retrieved_chunks": 0,
            }
            
        ranked_docs=reranker_service.rerank(request.question,docs)
        
        context,top_docs=context_builder_service.build_context(ranked_docs)
        history=memory_service.build_history()
        
        answer=generation_service.generate(request.question,context,history,)
        
        memory_service.save_conversation(request.question,answer,)
        
        sources=source_service.build_sources(top_docs)
       
        confidence=confidence_service.calculate(ranked_docs) 
              
        return {
            'answer':answer,
            'confidence':confidence,
            'sources':sources,
            'retrieved_chunks':len(top_docs),
        }        
            
chat_service=ChatService()        