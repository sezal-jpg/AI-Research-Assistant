from pathlib import Path
import json
from langchain_core.documents import Document
from app.core.logger import logger

class JsonLoader:
    def load(self,file_path:Path):
        logger.info(f'Loading JSON:{file_path.name}')
        with open(file_path,'r',encoding='utf-8') as file:
            data=json.load(file)
            content=json.dumps(data,indent=2,ensure_ascii=False)
       
        return [
            Document(page_content=content,metadata={'source_file':file_path.name,'source_type':'json',})
        ]    
        
json_loader=JsonLoader()      