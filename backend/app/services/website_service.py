from urllib.parse import urlparse
import requests
import tempfile
import os
import json
from PIL import Image
from app.core.logger import logger
from app.services.website_loader import website_loader
from app.services.crawler_service import crawler_service
from app.services.indexing_service import indexing_service
from app.core.app_state import state
from app.services.content_safety_service import content_safety_service

class WebsiteService:

    def upload(self, request):
        logger.info(f"Website received: {request.url}")
        
        existing_sources={
            chunk.metadata.get('source_file')
            for chunk in state.all_chunks
            if chunk.metadata.get('source_file')
        }
        if request.url in existing_sources:
            logger.info(f'Skipping already indexed website: {request.url}')
            
            return {"message":"Website already indexed",
                    'document':0,
                    'chunks':0}

        if request.crawl:
            docs = crawler_service.crawl(
                request.url,
                request.max_pages
            )
        else:
            docs = website_loader.load(
                request.url
            )

        if not docs:
            return {
                "message": "No documents found"
            }
            
        logger.info(
            "Running website media content safety check" )

        for doc in docs:
            image_urls = doc.metadata.get(
                "image_urls", []
            )
            video_urls = doc.metadata.get(
                "video_urls", []
            )
            
            if isinstance(image_urls,str):
                try:
                    image_urls=json.loads(image_urls)
                except json.JSONDecodeError:
                    image_urls=[]    
                    
            if isinstance(video_urls,str):
                try:
                    video_urls=json.loads(video_urls)
                except json.JSONDecodeError:
                    video_urls=[]            

            for image_url in image_urls:

                logger.info(
                    f"Checking website image: {image_url}"
                )
                
                image_extension = os.path.splitext(urlparse(image_url).path)[1].lower()
                
                if image_extension == ".svg":
                  logger.info(f"Skipping SVG website image: {image_url}" )
                  continue

                try:
                    response = requests.get(
                        image_url,
                        timeout=15,
                        headers={
                            "User-Agent": "OmniResearch-AI/1.0"
                        }
                    )
                    response.raise_for_status()

                    with tempfile.NamedTemporaryFile(
                        suffix=os.path.splitext(
                            urlparse(image_url).path
                        )[1] or ".jpg",
                        delete=False
                    ) as temp_file:

                        temp_file.write(
                            response.content
                        )
                        image_path = temp_file.name

                    try:
                        with Image.open(image_path) as image:
                            width,height=image.size
                            
                        if width<=1 or height <=1:
                            logger.info(f'Skipping tiny website image:' 
                                        f'{image_url} ({width}x{height})')  
                            continue  
                                                    
                        safety_result = (
                            content_safety_service.check_image(
                                image_path
                            )
                        )

                        if not safety_result["safe"]:
                            if safety_result.get('scan_error'):
                                logger.warning(f'Website content could not be processed'
                                               'because an image could not be analyzed for content safety')

                            logger.warning(
                                f"Unsafe website image blocked: "
                                f"{image_url}"
                            )

                            raise ValueError(
                                "Website content was blocked because "
                                "an image was detected as sexually "
                                "explicit or otherwise unsafe."
                            )

                    finally:
                        if os.path.exists(image_path):
                            os.remove(image_path)

                except ValueError:
                    raise

                except Exception as e:
                    logger.error(
                        f"Website image safety check failed: "
                        f"{image_url}: {e}"
                    )

                    raise ValueError(
                        "Website content was blocked because "
                        "an image could not be safely checked."
                    )

        
            for video_url in video_urls:
                logger.info(
                    f"Checking website video: {video_url}"
                )

                try:
                    response = requests.get(
                        video_url,
                        timeout=30,
                        headers={
                            "User-Agent": "OmniResearch-AI/1.0"
                        }
                    )
                    response.raise_for_status()

                    with tempfile.NamedTemporaryFile(
                        suffix=os.path.splitext(
                            urlparse(video_url).path
                        )[1] or ".mp4",
                        delete=False
                    ) as temp_file:

                        temp_file.write(
                            response.content
                        )
                        video_path = temp_file.name
                    try:
                        safety_result = (
                            content_safety_service.check_video(
                                video_path
                            )
                        )

                        if not safety_result["safe"]:
                            if safety_result.get('scan_error'):
                                logger.warning(f'Website video could not be analyzed:',
                                               f'{video_url}')
                                
                                raise ValueError(   "Website content could not be processed "
                                               "because a video could not be analyzed "
                                                  "for content safety.")
                                
                            logger.warning(
                                f"Unsafe website video blocked: "
                                f"{video_url}"
                            )

                            raise ValueError(
                                "Website content was blocked because "
                                "a video was detected as sexually "
                                "explicit or otherwise unsafe."
                            )

                    finally:
                        if os.path.exists(video_path):
                            os.remove(video_path)

                except ValueError:
                    raise

                except Exception as e:

                    logger.error(
                        f"Website video safety check failed: "
                        f"{video_url}: {e}"
                    )

                    raise ValueError(
                        "Website content was blocked because "
                        "a video could not be safely checked."
                    )

        logger.info(
            "Website media content safety check passed"
        )
                        
        for doc in docs:
            doc.metadata['source_file']=request.url    
            
        logger.info(
            "Running text content safety check "
            "for website content" )

        for doc in docs:

            if (
                doc.page_content
                and doc.page_content.strip()  ):

                safety_result = (
                    content_safety_service.check_text(
                        doc.page_content
                    ) )

                if not safety_result["safe"]:

                    logger.warning(
                        f"Unsafe website content blocked: "
                        f"{request.url}" )

                    raise ValueError(
                        "Website content was blocked because "
                        "it was detected as sexually explicit "
                        "or otherwise unsafe."
                    )

        logger.info(
            "Website content safety check passed"  )  

        chunks = indexing_service.index_documents(docs)

        return {
            "message": "Website indexed successfully",
            "documents": len(docs),
            "chunks": len(chunks)
        }

website_service = WebsiteService()