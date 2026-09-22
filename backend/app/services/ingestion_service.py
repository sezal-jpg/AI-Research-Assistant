import os
from typing import List
from pathlib import Path
from fastapi import UploadFile
from langchain_core.documents import Document
from app.core.logger import logger
from app.core.app_state import state
from app.services.indexing_service import indexing_service
from app.services.loader_factory import loader_factory
from app.services.youtube_service import youtube_service
from app.services.content_safety_service import content_safety_service

class IngestionService:

    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

        self.large_file_size_mb = float(
            os.getenv("LARGE_FILE_SIZE_MB", "20")
        )

    async def save_uploaded_files(
        self,
        files: List[UploadFile],
        existing_sources: set
    ) -> List[Path]:

        saved_files = []

        for file in files:

            filename = Path(
                file.filename or "uploaded_file"
            ).name

            if filename in existing_sources:
                logger.info(
                    f"Skipping already indexed file: {filename}"
                )
                continue

            file_path = self.upload_dir / filename
            logger.info(
                f"saving {filename}"
            )

            with open(file_path, "wb") as f:

                while True:

                    chunk = await file.read(
                        1024 * 1024 )
                    if not chunk:
                        break

                    f.write(chunk)

            file_size_mb = (
                file_path.stat().st_size
                / (1024 * 1024)
            )

            logger.info(
                f"Saved {filename} "
                f"({file_size_mb:.2f} MB)"
            )

            if file_size_mb >= self.large_file_size_mb:

                logger.warning(
                    f"Large file detected: {filename} "
                    f"({file_size_mb:.2f} MB). "
                    f"Large files may require more processing "
                    f"and may consume additional Gemini quota "
                    f"depending on enabled features."
                )

            saved_files.append(file_path)

        return saved_files

    async def process_documents(
        self,
        files: List[UploadFile] ):

        existing_sources = {
            chunk.metadata.get("source_file")
            for chunk in (state.all_chunks or [])
            if chunk.metadata.get("source_file")
        }

        saved_files = await self.save_uploaded_files(
            files,
            existing_sources
        )

        all_docs = []

        image_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".webp"
        }

        video_extensions = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".webm"
        }

        for file_path in saved_files:

            logger.info(
                f"Processing {file_path.name}"
            )

            suffix = file_path.suffix.lower()


            if suffix in image_extensions:

                logger.info(
                    f"Running content safety check "
                    f"for image: {file_path.name}"
                )

                safety_result = (
                    content_safety_service.check_image(
                        str(file_path)
                    )
                )

                if not safety_result["safe"]:
                    
                    file_path.unlink(
                        missing_ok=True
                    )
                    
                    if safety_result.get('scan_error'):
                        logger.error( f"Image safety analysis failed: "
                                       f"{file_path.name}: "
                                       f"{safety_result.get('error')}")
                        
                        raise ValueError("The image could not be fully analyzed "
                                         "for content safety.")
                        
                    logger.warning(f'insafe image blocked:'
                                   f'{file_path.name}')    

                    raise ValueError(
                        "Upload blocked because the image "
                        "was detected as sexually explicit "
                        "or otherwise unsafe."
                    )

                logger.info(
                    f"Image safety check passed: "
                    f"{file_path.name}"
                )

            elif suffix in video_extensions:

                logger.info(
                    f"Running content safety check "
                    f"for video: {file_path.name}"
                )

                safety_result = (
                    content_safety_service.check_video(
                        str(file_path)
                    )
                )

                if not safety_result["safe"]:

                    file_path.unlink(
                        missing_ok=True
                    )
                    
                    if safety_result.get('scan_error'):
                        logger.error(f"Video safety analysis failed:"
                                     f"{file_path.name}:"
                                     f"{safety_result.get('error')}")
                        
                        raise ValueError("The video could not be fully analyzed "
                                         "for content safety.")
                        
                    logger.warning( f"Unsafe video blocked:" 
                                   f"{file_path.name}")    

                    raise ValueError(
                        "Upload blocked because the video "
                        "was detected as sexually explicit "
                        "or otherwise unsafe."
                    )

                logger.info(
                    f"Video safety check passed: "
                    f"{file_path.name}"
                )

            elif suffix == ".pdf":

                logger.info(
                    f"Running PDF embedded image safety check "
                    f"for: {file_path.name}"
                )

                safety_result = (
                    content_safety_service
                    .check_pdf_embedded_images(
                        str(file_path)
                    )
                )

                if not safety_result["safe"]:

                    file_path.unlink(
                        missing_ok=True
                    )

                    if safety_result.get("scan_error"):

                        logger.warning(
                            f"PDF safety scan failed: "
                            f"{file_path.name}"
                        )

                        raise ValueError(
                            "The PDF could not be fully analyzed "
                            "for content safety because an embedded "
                            "image could not be processed."
                        )

                    logger.warning(
                        f"Unsafe PDF embedded image blocked: "
                        f"{file_path.name}"
                    )

                    raise ValueError(
                        "Upload blocked because the PDF "
                        "contains a sexually explicit or "
                        "otherwise unsafe embedded image."
                    )

                logger.info(
                    f"PDF embedded image safety check passed: "
                    f"{file_path.name}"
                )

            elif suffix in {".docx", ".pptx"}:

                logger.info(
                    f"Running embedded image safety check "
                    f"for: {file_path.name}"
                )

                safety_result = (
                    content_safety_service
                    .check_document_embedded_images(
                        str(file_path)
                    )
                )

                if not safety_result["safe"]:

                    file_path.unlink(
                        missing_ok=True
                    )
                    
                    if safety_result.get('scan_error'):
                        logger.error(f"Embedded image safety analysis failed: "
                                     f"{file_path.name}: "
                                     f"{safety_result.get('error')}")
                        
                        raise ValueError( "The document could not be fully analyzed "
                                         "because an embedded image could not be processed.")
                        
                    logger.warning(f"Unsafe embedded image blocked: "
                                    f"{file_path.name}")    

                    raise ValueError(
                        "Upload blocked because the document "
                        "contains a sexually explicit or "
                        "otherwise unsafe embedded image."
                    )

                logger.info(
                    f"Embedded image safety check passed: "
                    f"{file_path.name}"
                )

            loader = loader_factory.get_loader(
                file_path
            )

            if loader is None:

                logger.warning(
                    f"Unsupported file: "
                    f"{file_path.name}"
                )

                continue

            docs = loader.load(
                file_path
            )

            docs = self.add_metadata(
                docs,
                file_path.name
            )

            if docs:

                combined_text = "\n\n".join(
                    doc.page_content
                    for doc in docs
                    if doc.page_content
                    and doc.page_content.strip()
                )

                if combined_text.strip():

                    logger.info(
                        f"Running text content safety "
                        f"check for: {file_path.name}"
                    )

                    safety_result = (
                        content_safety_service.check_text(
                            combined_text
                        )
                    )

                    if not safety_result["safe"]:
                        
                        file_path.unlink(missing_ok=True)
                        
                        if safety_result.get('error'):
                            logger.error(f"Text content safety analysis failed: "
                                  f"{file_path.name}: "
                                  f"{safety_result['error']}")
                            
                            raise ValueError( "The document could not be fully processed "
                                              "because its text could not be analyzed "
                                              "for content safety.")

                        logger.warning(
                            f"Unsafe text content blocked: "
                            f"{file_path.name}"
                        )

                        raise ValueError(
                            "Upload blocked because the document "
                            "was detected as containing sexually "
                            "explicit or otherwise unsafe content."
                        )

                    logger.info(
                        f"Text content safety check passed: "
                        f"{file_path.name}"
                    )

            all_docs.extend(
                docs
            )

        chunks = indexing_service.index_documents(
            all_docs
        )

        logger.info(
            f"total documents : {len(all_docs)}"
        )

        logger.info(
            f"total chunks : {len(chunks)}"
        )

        return {
            "message": "Documents indexed successfully",
            "uploaded_files": len(saved_files),
            "documents": len(all_docs),
            "chunks": len(chunks),
        }

    async def process_youtube(
        self,
        url: str):

        logger.info(
            f"Processing YouTube URL: {url}"
        )

        video_id = youtube_service.extract_video_id(
            url
        )

        if not video_id:

            logger.error(
                "Could not extract YouTube video ID"
            )

            return {
                "message": "Invalid YouTube URL",
                "documents": 0,
                "chunks": 0
            }

        existing_sources = {
            chunk.metadata.get("source_file")
            for chunk in (state.all_chunks or [])
            if chunk.metadata.get("source_file")
        }

        youtube_source = f"youtube:{video_id}"

        if youtube_source in existing_sources:

            logger.info(
                f"Skipping already indexed YouTube video: "
                f"{video_id}"
            )

            return {
                "message": "YouTube video already indexed",
                "documents": 0,
                "chunks": 0
            }

        docs = youtube_service.get_transcript(
            url
        )

        if not docs:

            logger.warning(
                "No YouTube transcript found"
            )

            return {
                "message": "could not extract YouTube transcript",
                "documents": 0,
                "chunks": 0,
            }

        for doc in docs:

            doc.metadata["source_file"] = (
                youtube_source
            )

            doc.metadata["source_url"] = url
            doc.metadata["video_id"] = video_id

        combined_text = "\n\n".join(
            doc.page_content
            for doc in docs
            if doc.page_content
            and doc.page_content.strip()
        )

        if combined_text.strip():

            logger.info(
                "Running text content safety "
                "check for YouTube transcript"
            )

            safety_result = (
                content_safety_service.check_text(
                    combined_text
                )
            )

            if not safety_result["safe"]:
                if safety_result.get('error'):
                    logger.error( "YouTube transcript safety analysis " 
                                 "failed: "
                                 f"{safety_result['error']}")
                    
                    raise ValueError(  "YouTube content could not be fully "
                                      "processed because the transcript "
                                      "could not be analyzed for content safety.")

                logger.warning(
                    "Unsafe YouTube transcript blocked"
                )

                raise ValueError(
                    "YouTube content was blocked because "
                    "the transcript was detected as sexually "
                    "explicit or otherwise unsafe."
                )

            logger.info(
                "YouTube transcript safety check passed"
            )

        chunks = indexing_service.index_documents(
            docs
        )

        logger.info(
            f"YouTube documents: {len(docs)}"
        )

        logger.info(
            f"YouTube chunks: {len(chunks)}"
        )

        return {
            "message": "YouTube indexed successfully",
            "documents": len(docs),
            "chunks": len(chunks),
        }

    async def process_youtube_transcript(
        self,
        url: str,
        transcript: str
    ):

        logger.info(
            f"Processing youtube transcript: {url}"
        )

        video_id = youtube_service.extract_video_id(
            url
        )

        if not video_id:

            logger.error(
                "could not extract YouTube video ID"
            )

            return {
                "message": "Invalid Youtube URL",
                "documents": 0,
                "chunks": 0
            }

        existing_sources = {
            chunk.metadata.get("source_file")
            for chunk in (state.all_chunks or [])
            if chunk.metadata.get("source_file")
        }

        youtube_source = f"youtube:{video_id}"

        if youtube_source in existing_sources:

            logger.info(
                f"Skipping already indexed YouTube video:"
                f"{video_id}"
            )

            return {
                "message": "YouTube video already indexed",
                "documents": 0,
                "chunks": 0
            }

        transcript = transcript.strip()

        if not transcript:

            logger.warning(
                "Youtube transcript is empty"
            )

            return {
                "message": "Youtube transcript is empty",
                "documents": 0,
                "chunks": 0
            }

        logger.info(
            "Running text content safety check "
            "for YouTube transcript"
        )

        safety_result = (
            content_safety_service.check_text(
                transcript
            )
        )

        if not safety_result["safe"]:
            if safety_result.get('error'):
                logger.error("YouTube transcript safety analysis "
                             "failed: "
                            f"{safety_result['error']}")
                
                raise ValueError("YouTube content could not be fully "
                                 "processed because the transcript "
                                  "could not be analyzed for content safety.")

            logger.warning(
                "Unsafe YouTube transcript blocked"
            )

            raise ValueError(
                "YouTube content was blocked because "
                "the transcript was detected as sexually "
                "explicit or otherwise unsafe."
            )

        logger.info(
            "YouTube transcript safety check passed"
        )

        docs = [
            Document(
                page_content=transcript,
                metadata={
                    "source_type": "youtube",
                    "source_file": f"youtube:{video_id}",
                    "source_url": url,
                    "video_id": video_id,
                }
            )
        ]

        chunks = indexing_service.index_documents(
            docs
        )
        logger.info(
            f"YouTube transcript documents: "
            f"{len(docs)}"
        )

        logger.info(
            f"YouTube transcript chunks: "
            f"{len(chunks)}"
        )

        return {
            "message": "YouTube indexed successfully",
            "documents": len(docs),
            "chunks": len(chunks)
        }

    def add_metadata(
        self,
        docs,
        filename ):

        for doc in docs:

            doc.metadata["source_file"] = filename

        return docs

ingestion_service = IngestionService()