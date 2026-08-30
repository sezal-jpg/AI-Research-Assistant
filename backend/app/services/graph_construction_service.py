from app.core.logger import logger
from app.services.entity_extraction_service import(entity_extraction_service)
from app.services.relationship_extraction_service import(relationship_extraction_service)
from app.services.graph_service import graph_service

class GraphConstructionService:
    
    def __init__(self):
        self.processed_chunks=set()
    
    def build_from_document(self,document):
        text=document.page_content
        
        if not text or not text.strip():
            return
        text=text.strip()
        
        if text in self.processed_chunks:
            logger.info('Graph construction skipped:'
                        "chunk already processed")
            return
        
        logger.info('Building graph from document chunk')
        
        entities=entity_extraction_service.extract_entities(text)
        if not entities:
            logger.info('No entities extracted')
            self.processed_chunks.add(text)
            return
        
        graph_service.add_entities(entities)
        
        relationships=(relationship_extraction_service.extract_relationships(text,entities))
        
        graph_service.add_relationships(relationships)
        self.processed_chunks.add(text)
        
        logger.info(f'Graph construction completed:'
                    f"{len(entities)} entities,"
                    f"{len(relationships)} relationships")
       
graph_construction_service=(GraphConstructionService())    
        
        
    