from PIL import Image
from transformers import BlipProcessor,BlipForConditionalGeneration
from app.core.logger import logger

class BLIPService:
    def __init__(self):
        
        logger.info('Loading BLIP model')
        self.processor=BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model=BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        logger.info('BLIP model loaded successfully')
        
    def generate_caption(self,image_path:str):
        logger.info(f'Generating BLIP caption: {image_path}')    
        
        try:
            image=Image.open(image_path).convert('RGB')
            inputs=self.processor(images=image,return_tensors='pt')
            output=self.model.generate(**inputs,max_new_tokens=50)
            
            caption=self.processor.decode(output[0],skip_special_tokens=True)
            logger.info(f'BLIP caption:{caption}')
            
            return caption
        
        except Exception as e:
            logger.error(f'BLIP failed :{e}')
            
            return ""
        
blip_service=BLIPService()        