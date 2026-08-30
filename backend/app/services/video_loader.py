from pathlib import Path
import cv2
from langchain_core.documents import Document
from app.core.logger import logger
from app.services.whisper_service import whisper_service
from app.services.ocr_services import ocr_service
from app.services.blip_service import blip_service

class VideoLoader:
    
    def load(self,file_path:Path):
        logger.info(f'Loading Video: {file_path.name}')
        
        documents=[]
        transcript=whisper_service.transcribe(str(file_path))
        if transcript.strip():
            documents.append(Document(page_content=transcript,metadata={'source_file':file_path.name,'source_type':'video','content_type':'transcript',}))
            
        cap=cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            
            logger.error(f'Could not open video:' f"{file_path.name}") 
            return documents
        fps=cap.get(cv2.CAP_PROP_FPS) 
        frame_count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        duration=(frame_count/fps if fps else 0) 
        
        logger.info(f'Video Duration: {duration:.2f} seconds')
        
        interval=10
        current_time=0
        frame_number=0
        
        while current_time < duration:
            cap.set(cv2.CAP_PROP_POS_MSEC,current_time*1000)
            
            success,frame=cap.read()
            if not success:
                break
            frame_path=(Path('temp_frames')/f'{file_path.stem}_{frame_number}.jpg')
            frame_path.parent.mkdir(exist_ok=True)
            
            text=ocr_service.extract_text(str(frame_path))
            
            caption=blip_service.generate_caption(str(frame_path))
            combined=[]
            if text.strip():
                combined.append(f'Visible text: {text}')
                
            if caption.strip():
                combined.append(f'Visual description: {caption}') 
                
            if combined:
                documents.append(Document(page_content='\n'.jooin(combined),metadata={'source_file':file_path.name,'source_type':'video','timestamp':current_time,}))    
            
            frame_number+=1
            current_time+=interval
            
        cap.release()
        logger.info(f'Extracted {frame_number}'f'video frames') 
        logger.info(f'video produced' f'{len(documents)} documents')  
        
        return documents
    
video_loader=VideoLoader()            
            
             