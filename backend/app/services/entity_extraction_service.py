import json
from app.core.config import model
from app.core.logger import logger
from app.core.gemini_utils import log_gemini_error

class EntityExtractionService:
    
    def __init__(self):
        self.cache={}
    
    def extract_entities(self,text):
        if not text or not text.strip():
            return []
        text=text.strip()
        
        if text in self.cache:
            logger.info('entity extraction cache hit')
            return self.cache[text]
        
        prompt=f"""
You are an entity extraction system for an AI Research Assistant.

Extract the important entities from the given text.

For every entity return:
- name
- type

Allowed entity types:
Person
Organization
Technology
Location
Project
Method
Concept

Do not invent entities.
Only extract entities explicitly present in the text.

Return ONLY valid JSON in this format:

[
    {{
        "name": "entity name",
        "type": "entity type"
    }}
]

TEXT:
{text}
"""
        try:
            logger.info('Entity extraction Gemini call started')
            response=model.generate_content(prompt)
            result=response.text.strip()
         
            if result.startswith("```"):
             result=result.replace("```json","")
             result=result.replace("```","")
             result=result.strip()
             
            entities=json.loads(result) 
            if not isinstance(entities,list):
             logger.warning('Entity extraction did not return a list')
             return [] 
         
            self.cache[text]=entities 
                  
            logger.info(f'Extracted {len(entities)} entities')
            return entities
        
        except Exception as e:
            error_type=log_gemini_error('entity extraction',e)
            return []
        
entity_extraction_service=EntityExtractionService()        
       
       