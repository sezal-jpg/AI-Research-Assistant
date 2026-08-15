from PIL import Image
from app.core.config import model
from app.core.logger import logger

class VisionService:
    
    def analyze_image(self,image_path:str):
        logger.info(f'Analyzing image: {image_path}')
        image=Image.open(image_path)
        prompt="""
You are an AI Research Assistant.

Analyze this image carefully.

Extract:

1. Visible text.
2. Tables.
3. Charts.
4. Graphs.
5. Scientific diagrams.
6. Equations.
7. Important observations.

Return a detailed description.
        
        """
        response=model.generate_content([prompt,image])
        return response.text
    
vision_service=VisionService()    
        