from app.core.logger import logger
from app.services.website_loader import website_loader
from app.services.crawler_service import crawler_service
from app.services.indexing_service import indexing_service
from app.services.content_safety_service import content_safety_service


class WebsiteService:

    def upload(self, request):

        logger.info(f"Website received: {request.url}")

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