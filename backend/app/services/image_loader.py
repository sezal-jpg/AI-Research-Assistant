from pathlib import Path
from langchain_core.documents import Document
from app.core.logger import logger
from app.core.app_state import state
from app.services.vision_service import vision_service
from app.services.ocr_services import ocr_service
from app.services.blip_service import blip_service
from app.services.clip_service import clip_service

class ImageLoader:
    
    def load(self,file_path:Path):
        logger.info(f'Loading image: {file_path.name}')
        
        extracted_text=ocr_service.extract_text(str(file_path))
        
        description=vision_service.analyze_image(str(file_path))
        
        caption=blip_service.generate_caption(str(file_path))
        
        clip_embedding=clip_service.image_embedding(str(file_path))
        state.clip_embeddings[file_path.name]=(clip_embedding)
        
        content_parts=[]
        
        if extracted_text.strip():
            content_parts.append('OCR Extracted Text: \n'+ extracted_text)
        
        if description.strip():
            content_parts.append('Gemini Vision Analysis:\n'+description) 
            
        if caption.strip():
            content_parts.append('BLIP Image Caption:\n'+ caption)    
            
        combined_content='\n\n'.join(content_parts)    
            
        docs=[
            Document(page_content=combined_content,metadata={'source_file':file_path.name,'source_type':'image',})
        ]       
            
        logger.info(f'Image processed successfully:'f"{file_path.name}")    
        
        return docs
        
image_loader=ImageLoader()        