import cv2
from PIL import Image
from pathlib import Path
from transformers import pipeline
from app.core.logger import logger
from pypdf import PdfReader
from io import BytesIO

NSFW_MODEL = "Falconsai/nsfw_image_detection"
TEXT_SAFETY_MODEL = "uget/sexual_content_dection"

NSFW_THRESHOLD = 0.90
TEXT_SAFETY_THRESHOLD = 0.90

VIDEO_SAMPLE_SECONDS = 1.0
MAX_VIDEO_SAFETY_FRAMES = 300

TEXT_CHUNK_WORDS = 100
TEXT_CHUNK_OVERLAP = 20


class ContentSafetyService:

    def __init__(self):
        self.classifier = None
        self.text_classifier = None

    def _load_classifier(self):

        if self.classifier is None:
            logger.info(
                "Loading NSFW content safety model..."   )

            self.classifier = pipeline(
                "image-classification",
                model=NSFW_MODEL,
                device=-1
            )

            logger.info(
                "NSFW content safety model loaded"   )

        return self.classifier

    def _load_text_classifier(self):

        if self.text_classifier is None:
            logger.info(
                "Loading text content safety model..."  )

            self.text_classifier = pipeline(
                "text-classification",
                model=TEXT_SAFETY_MODEL,
                device=-1
            )

            logger.info(
                "Text content safety model loaded"  )

        return self.text_classifier

    def check_image(
        self,
        image_path: str):

        logger.info(
            f"Running content safety check: "
            f"{image_path}"
        )

        try:

            image = Image.open(
                image_path
            ).convert("RGB")

            return self.check_image_object(
                image
            )

        except Exception as e:

            logger.error(
                f"Content safety check failed: {e}"
            )

            return {
                "safe": False,
                "nsfw_score": 0.0,
                "error": str(e),
                'scan_error':True
            }

    def check_image_object(
        self,
        image ):

        try:

            if not isinstance(
                image,
                Image.Image):
                image = Image.fromarray(image)

            image = image.convert("RGB")
            classifier = self._load_classifier()
            results = classifier(
                image,
                top_k=2)

            nsfw_score = 0.0

            for result in results:
                label = result["label"].lower()
                if label == "nsfw":

                    nsfw_score = float(
                        result["score"]
                    )

                    break

            is_unsafe = (
                nsfw_score >= NSFW_THRESHOLD
            )

            logger.info(
                f"Content safety result: "
                f"nsfw_score={nsfw_score:.4f}, "
                f"unsafe={is_unsafe}" )

            return {
                "safe": not is_unsafe,
                "nsfw_score": nsfw_score
            }

        except Exception as e:

            logger.error(
                f"Image content safety check failed: "
                f"{e}")

            return {
                "safe": False,
                "nsfw_score": 0.0,
                "error": str(e),
                'scan_error':True
            }

    def _split_text(
        self,
        text ):

        words = text.split()

        if not words:
            return []

        chunks = []

        start = 0
        total_words = len(words)

        while start < total_words:

            end = min(
                start + TEXT_CHUNK_WORDS,
                total_words  )

            chunk = " ".join(
                words[start:end]
            )

            if chunk.strip():
                chunks.append(chunk)

            if end >= total_words:
                break

            start = max(
                end - TEXT_CHUNK_OVERLAP,
                start + 1
            )

        return chunks

    def check_text(
        self,
        text: str ):

        logger.info(
            "Running text content safety check"  )

        if not text or not text.strip():

            return {
                "safe": True,
                "sexual_score": 0.0,
                "chunks_scanned": 0
            }

        try:

            classifier = self._load_text_classifier()

            text_chunks = self._split_text(
                text
            )

            highest_score = 0.0
            scanned_chunks = 0

            for index, chunk in enumerate(
                text_chunks,
                start=1 ):

                results = classifier(
                    chunk,
                    truncation=True
                )

                if not results:
                    continue

                result = results[0]
                logger.info(f'Raw text safety result: {result}')

                label = result[
                    "label"
                ].lower()

                score = float(
                    result["score"]  )

                sexual_score = (
                    score
                    if label in { "sexual","label_1"}
                    else 0.0
                )

                highest_score = max(
                    highest_score,
                    sexual_score
                )

                scanned_chunks += 1

                logger.info(
                    f"Text safety chunk "
                    f"{index}: "
                    f"sexual_score="
                    f"{sexual_score:.4f}"
                )

                if (
                    sexual_score
                    >= TEXT_SAFETY_THRESHOLD   ):

                    logger.warning(
                        "Sexually explicit "
                        "content detected in "
                        f"text chunk {index}"
                    )

                    return {
                        "safe": False,
                        "sexual_score": sexual_score,
                        "chunk": index,
                        "chunks_scanned":
                            scanned_chunks
                    }

            logger.info(
                "Text content safety scan "
                "completed: "
                f"chunks={scanned_chunks}, "
                f"highest_score="
                f"{highest_score:.4f}"
            )

            return {
                "safe": True,
                "sexual_score": highest_score,
                "chunks_scanned":
                    scanned_chunks
            }

        except Exception as e:

            logger.error(
                f"Text content safety check "
                f"failed: {e}"
            )

            return {
                "safe": False,
                "sexual_score": 1.0,
                "error": str(e)
            }

    def check_video(
        self,
        video_path: str
    ):

        logger.info(
            f"Running video content safety check: "
            f"{video_path}"
        )

        cap = cv2.VideoCapture(
            video_path
        )

        if not cap.isOpened():
            logger.error(
                f"Could not open video for safety "
                f"scan: {video_path}"  )

            return {
                "safe": False,
                "reason": "Could not open video"
            }

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        frame_count = cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )

        duration = (
            frame_count / fps
            if fps
            else 0
        )

        if duration <= 0:

            cap.release()

            return {
                "safe": False,
                "reason": "Invalid video duration"
            }

        interval = VIDEO_SAMPLE_SECONDS

        estimated_frames = int(
            duration / interval
        )

        if (
            estimated_frames
            > MAX_VIDEO_SAFETY_FRAMES):

            interval = (
                duration
                / MAX_VIDEO_SAFETY_FRAMES
            )

        classifier = self._load_classifier()

        current_time = 0.0
        scanned_frames = 0
        highest_score = 0.0

        try:

            while current_time < duration:

                cap.set(
                    cv2.CAP_PROP_POS_MSEC,
                    current_time * 1000   )

                success, frame = cap.read()

                if not success:
                    break

                frame_rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                image = Image.fromarray(
                    frame_rgb
                )

                results = classifier(
                    image,
                    top_k=2
                )

                frame_score = 0.0

                for result in results:

                    if (
                        result["label"]
                        .lower()
                        == "nsfw"
                    ):

                        frame_score = float(
                            result["score"]
                        )

                        break

                highest_score = max(
                    highest_score,
                    frame_score
                )

                scanned_frames += 1

                logger.info(
                    f"Safety frame "
                    f"{scanned_frames}: "
                    f"time={current_time:.2f}s, "
                    f"nsfw_score="
                    f"{frame_score:.4f}"
                )

                if (
                    frame_score
                    >= NSFW_THRESHOLD):

                    logger.warning(
                        "Unsafe content detected "
                        "in video at "
                        f"{current_time:.2f}s"
                    )

                    return {
                        "safe": False,
                        "nsfw_score":
                            frame_score,
                        "timestamp":
                            current_time,
                        "frames_scanned":
                            scanned_frames
                    }

                current_time += interval
                
        except Exception as e:
            logger.error(f'Video content safety'
                         f'analysis failed: {e}')
            
            return {
                 "safe": False,
                "nsfw_score": 0.0,
                "frames_scanned":
                    scanned_frames,
                "reason":
                    "Video could not be "
                    "fully analyzed.",
                "error": str(e),
                "scan_error": True
            }    

        finally:

            cap.release()

        logger.info(
            "Video safety scan completed: "
            f"frames={scanned_frames}, "
            f"highest_nsfw_score="
            f"{highest_score:.4f}"
        )

        return {
            "safe": True,
            "nsfw_score": highest_score,
            "frames_scanned":
                scanned_frames
        }
        
    def check_pdf_embedded_images(self, file_path: str) -> dict:

        logger.info(
            f"Running PDF embedded image safety check: "
            f"{file_path}" )

        try:
            reader = PdfReader(file_path)
            total_images = 0
            logger.info(
                f"PDF contains {len(reader.pages)} pages")

            for page_number, page in enumerate(
                reader.pages,
                start=1):

                images = getattr(
                    page,
                    "images",
                    [] )

                for image in images:

                    total_images += 1
                    logger.info(
                        f"Scanning PDF embedded image "
                        f"{total_images} "
                        f"from page {page_number}" )

                    try:
                        image_data = image.data

                        pil_image = (
                            Image.open(
                                BytesIO(image_data)
                            ).convert("RGB") )

                        result = (
                            self.check_image_object(
                                pil_image
                            )  )

                        if not result["safe"]:

                            logger.warning(
                                f"Unsafe embedded image "
                                f"detected in PDF: "
                                f"{Path(file_path).name}, "
                                f"page={page_number}" )

                            return {
                                "safe": False,
                                "nsfw_score": result.get(
                                    "nsfw_score",
                                    1.0
                                ),
                                "page": page_number,
                                "images_scanned":
                                    total_images,
                                "reason":
                                    "Unsafe embedded image "
                                    "detected."
                            }

                    except Exception as image_error:

                        logger.error(
                            f"Failed to scan PDF embedded "
                            f"image on page "
                            f"{page_number}: "
                            f"{image_error}"
                        )

                        return {
                            "safe": False,
                            "nsfw_score": 0.0,
                            "page": page_number,
                            "images_scanned":total_images,
                            "reason":
                                "PDF embedded image "
                               "could not be analyzed.",
                                "error": str(image_error),
                                "scan_error": True
                        }

            logger.info(
                f"PDF embedded image safety scan "
                f"completed: "
                f"images={total_images}"
            )

            return {
                "safe": True,
                "nsfw_score": 0.0,
                "images_scanned": total_images,
                "reason":
                    "No unsafe embedded images detected."
            }

        except Exception as e:

            logger.error(
                f"PDF embedded image safety scan "
                f"failed for {file_path}: {e}"
            )

            return {
                "safe": False,
                "nsfw_score": 0.0,
                "reason":
                    "PDF embedded image safety scan failed.",
                "error": str(e),
                'scan_error':True
            }    
        
    def check_document_embedded_images(self, file_path: str) -> dict:

     try:
        from zipfile import ZipFile
        from io import BytesIO
        from PIL import Image

        extension = Path(file_path).suffix.lower()

        if extension == ".docx":
            media_prefix = "word/media/"

        elif extension == ".pptx":
            media_prefix = "ppt/media/"

        else:
            return {
                "safe": True,
                "nsfw_score": 0.0,
                "reason": "Embedded image scanning not required for this file type."
            }

        with ZipFile(file_path, "r") as archive:
            image_files = [
                name for name in archive.namelist()
                if name.startswith(media_prefix)
            ]

            logger.info(
                f"Embedded image safety scan: {Path(file_path).name} "
                f"({len(image_files)} images found)"
            )

            for image_name in image_files:
                try:
                    if Path(image_name).suffix.lower()=='.svg':
                        logger.info(f'Skipping SVG embedded image: {image_name}')
                        continue
                    
                    image_data = archive.read(image_name)
                    image = Image.open(BytesIO(image_data)).convert("RGB")

                    result = self.check_image_object(image)
                    
                    if result.get("error"):
                        logger.error(
                        f"Embedded image safety analysis failed "
                        f"for {image_name}: "
                        f"{result['error']}" )
                        
                        return {
                        "safe": False,
                       "nsfw_score": 0.0,
                       "reason":
                        "Embedded image could not be analyzed.",
                        "error": result["error"],
                        "scan_error": True }

                    if not result["safe"]:
                        logger.warning(
                            f"Unsafe embedded image detected in "
                            f"{Path(file_path).name}: {image_name}"
                        )

                        return {
                            "safe": False,
                            "nsfw_score": result.get("nsfw_score", 1.0),
                            "reason": "Unsafe embedded image detected."
                        }

                except Exception as image_error:
                    logger.error(
                        f"Failed to scan embedded image "
                        f"{image_name}: {image_error}"
                    )

                  
                    return {
                        "safe": False,
                        "nsfw_score": 0.0,
                        "reason":
                            "Embedded image could not be analyzed.",
                      "error": str(image_error),
                       "scan_error": True
                    }

        return {
            "safe": True,
            "nsfw_score": 0.0,
            "reason": "No unsafe embedded images detected."
        }

     except Exception as e:
        logger.error(
            f"Embedded image safety scan failed for "
            f"{file_path}: {e}"
        )

        return {
            "safe": False,
            "nsfw_score": 0.0,
            "reason": "Embedded image safety scan failed.",
            'error':str(e),
            'scan_error':True
        }    

content_safety_service = (ContentSafetyService())