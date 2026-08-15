from pathlib import Path
from langchain_core.documents import Document
from app.core.logger import logger

class MarkdownLoader:
    def load(self,file_path:Path):
        logger.info(f'Loading Markdown:{file_path.name}')
        with open(file_path,'r',encoding='utf-8') as file:
            content=file.read()
            
        if not content.strip():
            return []
        return [
            Document(page_content=content,metadata={'source_file':file_path.name,'source_type':'markdown',})
        ]    
        
markdown_loader=MarkdownLoader()      