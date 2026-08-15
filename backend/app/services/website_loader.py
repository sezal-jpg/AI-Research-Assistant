from langchain_community.document_loaders import WebBaseLoader
from app.core.logger import logger

class WebsiteLoader:
    
    def load(self, url:str):
        logger.info(f'Loading Website: {url}')
        loader=WebBaseLoader(url)
        docs=loader.load()
        for doc in docs:
            cleaned_metadata={}
            for key,value in doc.metadata.items():
                if isinstance(value,(str,int,float,bool)):
                    cleaned_metadata[key]=value
            doc.metadata=cleaned_metadata
            
            doc.metadata['source_url']=url
            doc.metadata['source_type']='website'        
        return docs
    
website_loader=WebsiteLoader()    