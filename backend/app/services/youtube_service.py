import re
import requests
from langchain_core.documents import Document
from app.core.logger import logger

class YouTubeService:

    def extract_video_id(self, url: str):
        patterns = [
            r"(?:v=)([a-zA-Z0-9_-]{11})",
            r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_transcript(self, url: str):
        video_id = self.extract_video_id(url)

        if not video_id:
            logger.error(f"Invalid YouTube URL: {url}")
            return []

        try:
            response = requests.get(
                "https://api.freetranscriptapi.com/v1/transcript",
                params={
                    "video_url": url,
                    "lang": "en",
                },
                timeout=60,
            )

            response.raise_for_status()
            data = response.json()
            transcript = data.get("transcript", [])

            if not transcript:
                logger.warning(
                    f"No transcript returned for YouTube video: {video_id}"
                )
                return []

            text_parts = []

            for segment in transcript:
                if isinstance(segment, dict):
                    text = segment.get("text", "").strip()

                    if text:
                        text_parts.append(text)

                elif isinstance(segment, str):
                    text = segment.strip()

                    if text:
                        text_parts.append(text)

            text = " ".join(text_parts).strip()

            if not text:
                logger.warning(
                    f"Transcript contained no usable text: {video_id}"
                )
                return []

            title = data.get("title", "")

            logger.info(
                f"YouTube transcript retrieved successfully: "
                f"{video_id}, characters={len(text)}"
            )

            return [
                Document(
                    page_content=text,
                    metadata={
                        "source": url,
                        "source_type": "youtube",
                        "video_id": video_id,
                        "title": title,
                    },
                )
            ]

        except requests.RequestException as e:
            logger.error(
                f"FreeTranscriptAPI request failed for {video_id}: {e}"
            )
            return []

        except Exception as e:
            logger.error(
                f"YouTube transcript processing failed for {video_id}: {e}"
            )
            return []

youtube_service = YouTubeService()