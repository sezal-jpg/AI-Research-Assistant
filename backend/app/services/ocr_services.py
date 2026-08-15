import pytesseract
from PIL import Image
from app.core.logger import logger

pytesseract.pytesseract.tesseract_cmd=( r"C:\Program Files\Tesseract-OCR\tesseract.exe")

class OCRService:
    def extract_text(self,image_path:str):
        logger.info(f'Running OCR: {image_path}')
        
        try:
            image=Image.open(image_path)
            text=pytesseract.image_to_string(image,lang='eng')
            text=text.strip()
            
            logger.info(f'OCR extracted {len(text)} characters')
            return text
        except Exception as e:
            logger.error(f'OCR failed :{e}')
            
            return ""
        
ocr_service=OCRService()        
