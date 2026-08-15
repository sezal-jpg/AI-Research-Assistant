from app.core.logger import logger
from app.services.website_loader import website_loader
from app.services.crawler_service import crawler_service
from app.services.indexing_service import indexing_service


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

        chunks = indexing_service.index_documents(docs)

        return {
            "message": "Website indexed successfully",
            "documents": len(docs),
            "chunks": len(chunks)
        }


website_service = WebsiteService()