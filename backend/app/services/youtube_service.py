import re
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from app.core.logger import logger

class YouTubeService:
    def extract_video_id(self,url:str):
        patterns=[r"(?:v=)([a-zA-Z0-9_-]{11})",
            r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",]
        
        for pattern in patterns:
            match=re.search(pattern,url)
            
            if match:
                return match.group(1)
        return None
    
    def get_transcript(self,url:str):
        logger.info(f'Processing YouTube URL: {url}')
        
        video_id=self.extract_video_id(url)
        
        if not video_id:
            logger.error('Could not extract Youtube video ID')
            return []
        
        try:
            api=YouTubeTranscriptApi()
            transcript=api.fetch(video_id,languages=['en'])
            text=" ".join(item.text for item in  transcript) 
            
            text=text.strip()  
            if not text:
                logger.warning('YouTube transcript is empty')
                return []
            
            logger.info(f'YouTube transcript extracted:' f"{len(text)} characters")
            return[Document(page_content=text,metadata={
                 'source_type':'youtube',
                 'source_file':f"youtube:{video_id}",
                 'source_url':url,
                 'video_id':video_id,
             })] 
            
        except Exception as e:
            logger.error(f'YouTube transcript failed: {e}')
            return []
        
youtube_service=YouTubeService()            