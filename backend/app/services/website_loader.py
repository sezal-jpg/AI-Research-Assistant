from langchain_community.document_loaders import WebBaseLoader
from app.core.logger import logger
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebsiteLoader:

    def load(self, url: str):
        logger.info(f"Loading Website: {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()

        try:
            response = loader.web_paths[0] if hasattr(loader, "web_paths") else None
            import requests

            html_response = requests.get(
                url,
                timeout=15,
                headers={
                    "User-Agent": "OmniResearch-AI/1.0"
                }
            )
            html_response.raise_for_status()
            soup = BeautifulSoup(
                html_response.text,
                "html.parser"
            )

            image_urls = []
            video_urls = []

            for img in soup.find_all("img", src=True):
                image_url = urljoin(
                    url,
                    img.get("src")
                )

                if image_url.startswith(("http://", "https://")):
                    image_urls.append(image_url)

            for video in soup.find_all("video"):
                for source in video.find_all("source", src=True):

                    video_url = urljoin(
                        url,
                        source.get("src")
                    )

                    if video_url.startswith(("http://", "https://")):
                        video_urls.append(video_url)

                if video.get("src"):
                    video_url = urljoin(
                        url,
                        video.get("src")
                    )

                    if video_url.startswith(("http://", "https://")):
                        video_urls.append(video_url)

            image_urls = list(dict.fromkeys(image_urls))
            video_urls = list(dict.fromkeys(video_urls))

            logger.info(
                f"Website media discovered: "
                f"images={len(image_urls)}, "
                f"videos={len(video_urls)}"
            )

        except Exception as e:
            logger.warning(
                f"Failed to discover website media: {e}"
            )

            image_urls = []
            video_urls = []

        for doc in docs:
            cleaned_metadata = {}

            for key, value in doc.metadata.items():
                if isinstance(
                    value,
                    (str, int, float, bool)  ):
                    cleaned_metadata[key] = value

            doc.metadata = cleaned_metadata
            doc.metadata["source_url"] = url
            doc.metadata["source_type"] = "website"

            doc.metadata["image_urls"] = image_urls
            doc.metadata["video_urls"] = video_urls

        return docs
    
website_loader = WebsiteLoader()