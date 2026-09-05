import json
from app.core.config import model
from app.core.logger import logger
from app.core.gemini_utils import log_gemini_error

class EntityExtractionService:
    
    def __init__(self):
        self.cache={}
        self.quota_exhausted=False
    
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
            log_gemini_error('entity extraction',e)
            return []
        
    def extract_entities_batch(self,documents):
        if self.quota_exhausted:
            logger.warning('Skipping batch entity extraction because Gemini quota is exhausted')
            return []
        
        if not documents:
            return []
        
        valid_documents=[]
        for index,document in enumerate(documents):
            text=document.page_content.strip()
            if text:
                valid_documents.append((index,text))
        
        if not valid_documents:
            return []
        combined_text="\n\n".join(f""" CHUNK {index}: {text}""" for index,text in valid_documents)
        cache_key=('BATCH',combined_text)
        
        if cache_key in self.cache:
            logger.info('Batch entity extraction cache hit')     
            return self.cache[cache_key]  
        
        prompt= f"""
You are an entity extraction system for an AI Research Assistant.

Extract important entities from ALL the documents below.

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

Rules:

1. Extract only entities explicitly present in the documents.
2. Do not invent entities.
3. Avoid duplicate entities.
4. Combine identical entities into one entity.
5. Return ONLY valid JSON.

Format:

[
    {{  'chunk': 0,
         "name": "entity name",
        "type": "entity type"
    }}
]

DOCUMENTS:
{combined_text}
"""
        try:
            logger.info(f'Btch entity extraction Gemini call started'
                        f"for{len(valid_documents)} documents")
            
            response=model.generate_content(prompt)
            result=response.text.strip()
            
            if result.startswith("```"):
                result=result.replace("```json","")
                result=result.replace("```","")
                result=result.strip()
                
            entities=json.loads(result)
            if not isinstance(entities,list):
                logger.warning('Batch entity extraction did not return a list')
                return []
            
            valid_entities=[]
            valid_chunk_ids={
                index for index,_ in valid_documents
            }
            
            for entity in entities:
                if not isinstance(entity,dict):
                    continue
                
                chunk_id=entity.get('chunk')
                name=entity.get('name')
                entity_type=entity.get('type')
                
                if(chunk_id in valid_chunk_ids and name and entity_type):
                    valid_entities.append({'chunk':chunk_id,'name':name,'type':entity_type})
                       
            
            self.cache[cache_key]=valid_entities
            logger.info(f'Batch entity extraction returned'
                        f"{len(entities)} entities")
            
            return valid_entities    
        
        except Exception as e:
            error_type=log_gemini_error('batch entity extraction',e)
            if error_type=='quota':
                self.quota_exhausted=True
                logger.warning('gemini quota exhausted future grph entity extraction calls will be skipped')
            return []
              
        
entity_extraction_service=EntityExtractionService()        
       
       