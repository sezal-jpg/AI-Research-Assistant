import json
from app.core.config import model
from app.core.logger import logger
from app.core.gemini_utils import log_gemini_error

class RelationshipExtractionService:
    
    def __init__(self):
        self.cache={}
        
    def extract_relationships(self,text,entities):
        
        if not text or not text.strip():
            return []
        
        if not entities:
            return []
        text=text.strip()
        
        entity_names=[
            entity['name'] for entity in entities
            if 'name' in entity
        ]
        
        cache_key=(text,tuple(sorted(entity_names)))
        if cache_key in self.cache:
            logger.info('Relationship extraction cache hit')
            return self.cache[cache_key]
        
        prompt=f"""
You are a relationship extraction system for an AI Research Assistant.

Extract relationships ONLY between the entities provided below.

ENTITIES:
{entity_names}

TEXT:
{text}

Rules:

1. Use only entities present in the entity list.
2. Use only relationships explicitly supported by the text.
3. Do not invent relationships.
4. Do not use outside knowledge.
5. Return an empty list if no relationship is clearly present.

Return ONLY valid JSON in this format:

[
    {{
        "source": "entity 1",
        "relationship": "relationship name",
        "target": "entity 2"
    }}
]
"""
        try:
            logger.info('Relationship extraction Gemini call started')
            response=model.generate_content(prompt)
            result=response.text.strip()
            
            if result.startswith("```"):
                result=result.replace("```json","")
                result=result.replace('```',"")
                result=result.strip()
                
            relationships=json.loads(result)    
            if not isinstance(relationships,list):
                logger.warning('relationship extraction did not return a list')
                return []
            
            valid_relationships=[]
            for relationship in relationships:
                if not isinstance(relationship,dict):
                    continue
                
                source=relationship.get('source')
                relation=relationship.get('relationship')
                target=relationship.get('target')
                
                if(source in entity_names and target in entity_names and relation):
                    valid_relationships.append({'source':source,
                                                'relationship':relation,
                                                'target':target}) 
                    
            self.cache[cache_key]=(valid_relationships)    
            
            logger.info(f'Extracted {len(valid_relationships)} valid relationships')
            return valid_relationships
        
        except Exception as e:
           error_type=log_gemini_error('relationship extraction',e)
           return []    
        
relationship_extraction_service=RelationshipExtractionService()        