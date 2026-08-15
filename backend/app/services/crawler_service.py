from app.core.logger import logger
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
import requests
from app.services.website_loader import website_loader

class CrawlerService:
    
    def crawl(self,start_url:str,max_pages:int):
        logger.info(f'Starting Website Crawl: {start_url} |  max_pages= {max_pages}')
        visited=set()
        queue=[start_url]
        all_docs=[]
        base_domain=urlparse(start_url).netloc
        
        while queue and len(visited)<max_pages:
            current_url=queue.pop(0)
            if current_url in visited:
                continue
            try:
                logger.info(f'crawling: {current_url}')
                response=requests.get(current_url,timeout=15,headers={'User-Agent':'OmniResearch-AI/1.0'})
                response.raise_for_status()
                visited.add(current_url)
            
                docs=website_loader.load(current_url)
                for doc in docs:
                  doc.metadata['source_url']=current_url
                  doc.metadata['source_type']=website_loader
                all_docs.extend(docs)
            
                soup=BeautifulSoup(response.text,'html.parser')
            
                for link in soup.find_all('a',href=True):
                   next_url=urljoin(current_url,link['href'])
                   parsed=urlparse(next_url)
                
                   if parsed.scheme not in ['http','https']:
                     continue
                   if parsed.netloc!=base_domain:
                     continue
                   next_url=next_url.split('#')[0]
                
                   if next_url not in visited and next_url not in queue:
                     queue.append(next_url)
            except Exception as e:
              logger.error(f'Failed to crawl {current_url} :{e}')
              visited.add(current_url)
        logger.info(f'Crawl completed. Pages visited: {len(visited)}') 
        logger.info(f'Documents collected: {len(all_docs)}')
        
        return all_docs               
                    
crawler_service=CrawlerService()    
        