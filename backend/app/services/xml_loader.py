from pathlib import Path
import xml.etree.ElementTree as ET
from langchain_core.documents import Document
from app.core.logger import logger

class XmlLoader:
    
    def load(self,file_path:Path):
        logger.info(f'Loading XML:{file_path.name}')
        tree=ET.parse(file_path)
        root=tree.getroot()
        text_parts=[]
        for element in root.iter():
            if element.text:
                text=element.text.strip()
                if text:
                    text_parts.append(text)
                    
        content='\n'.join(text_parts)            
            
        if not content:
            return []
        return [
            Document(page_content=content,metadata={'source_file':file_path.name,'source_type':'xml',})
        ]    
        
xml_loader=XmlLoader()     