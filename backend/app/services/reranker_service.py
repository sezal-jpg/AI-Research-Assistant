from sentence_transformers import CrossEncoder
from app.core.logger import logger
class RerankerService:
    def __init__(self):
        logger.info('Loading CrossEncoder...')
        self.model=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info('CrossEncoder Loaded')
    
    def rerank(self,question,docs):
        if not docs:
            return []    
        pairs=[(question,doc.page_content) for doc in docs]
        scores=self.model.predict(pairs)
        ranked_docs=list(zip(docs,scores))
        ranked_docs.sort(key=lambda x: x[1],reverse=True)
        
        return ranked_docs
    
reranker_service=RerankerService()    