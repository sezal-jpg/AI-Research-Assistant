import torch
from PIL import Image
from transformers import CLIPProcessor,CLIPModel
from app.core.logger import logger

class CLIPService:
    
    def __init__(self):
        logger.info('Loading CLIP model...')
        self.device='cuda' if torch.cuda.is_available() else 'cpu'
        
        self.model=CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor=CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.to(self.device)
        
        logger.info(f'CLIP successfully on {self.device}')
        
    def image_embedding(self,image_path:str):
        logger.info(f'Generating CLIP image embedding :{image_path}')
        
        image=Image.open(image_path).convert('RGB') 
        inputs=self.processor(images=image,return_tensors='pt')
        
        with torch.no_grad():
            image_features=self.model.get_image_features(**inputs) 
            
        image_features=image_features/(image_features.norm(p=2,dim=-1,keepdim=True))
    
    def image_text_similarity(self,image_path:str,texts:list[str]):
        logger.info(f'Comparing image with {len(texts)} texts')
        
        image=Image.open(image_path).convert('RGB')
        inputs=self.processor(text=texts,images=image,return_tensors='pt',padding=True)
        
        with torch.no_grad():
            outputs=self.model(**inputs)
            probabilities=outputs.logits_per_image.softmax(dim=1)[0]
            
            results=[]
            
            for text,probability in zip(texts,probabilities):
                results.append({
                    'text':text,
                    'score':float(probability)
                })          
            results.sort(key=lambda item: item['score'],reverse=True)
            return results
        
clip_service = None


def get_clip_service():
    global clip_service

    if clip_service is None:
        clip_service = CLIPService()

    return clip_service   
            