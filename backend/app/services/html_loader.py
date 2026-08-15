from pathlib import Path
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from app.core.logger import logger

class HtmlLoader:
    
    def load(self,file_path:Path):
        logger.info(f'Loading HTML:{file_path.name}')
        with open(file_path,'r',encoding='utf-8') as file:
            html=file.read()
        
        soup=BeautifulSoup(html,'html.parser')
        for element in soup(['script','style','noscript']):
            element.decompose()
            
        content=soup.get_text(separator='\n')
            
        lines=[line.stript() for line in content.splitlines() if line.strip()]
        content='\n'.join(lines)
                
        if not content:
             return []
        return [
            Document(page_content=content,metadata={'source_file':file_path.name,'source_type':'html',})
        ]    
        
html_loader=HtmlLoader()    