from pathlib import Path
from app.services.document_loader import document_loader
from app.services.image_loader import image_loader
from app.services.docx_loader import docx_loader
from app.services.audio_loader import audio_loader
from app.services.pptx_loader import pptx_loader
from app.services.excel_loader import excel_loader
from app.services.csv_loader import csv_loader
from app.services.text_loader import text_loader
from app.services.markdown_loader import markdown_loader
from app.services.json_loader import json_loader
from app.services.html_loader import html_loader
from app.services.xml_loader import xml_loader
from app.services.ods_loader import ods_loader
from app.services.video_loader import video_loader

class LoaderFactory:
    
    def get_loader(self,file_path:Path):
        
        suffix=file_path.suffix.lower()
        if suffix=='.pdf':
            return document_loader
        
        if suffix in [".mp3",
            ".wav",
            ".m4a",
            ".flac",
            ".ogg",]:
            return audio_loader
        
        if suffix in [".mp4",
             ".avi",
              ".mov",
              ".mkv",
              ".webm",]:
            return video_loader
        
        if suffix in [ ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".webp",]:
             return image_loader
         
        if suffix=='.docx':
            return docx_loader
        
        if suffix=='.pptx':
            return pptx_loader
        
        if suffix in ['.xlsx','.xls',]:
            return excel_loader
        
        if suffix=='.ods':
            return ods_loader
        
        if suffix=='.csv':
            return csv_loader
        
        if suffix=='.txt':
            return text_loader
        
        if suffix in ['.md','.markdown',] :
            return markdown_loader
        
        if suffix=='.json':
            return json_loader
        
        if suffix in ['.html','.htm',]:
            return html_loader
        
        if suffix=='.xml':
            return xml_loader
        
        return None 
            
loader_factory=LoaderFactory()            
        