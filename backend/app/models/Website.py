from pydantic import BaseModel

class WebsiteRequest(BaseModel):
    url:str
    crawl: bool=False
    max_pages: int =10