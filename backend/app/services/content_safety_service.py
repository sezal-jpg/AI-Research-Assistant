from pathlib import Path
import cv2
from PIL import Image
from transformers import pipeline
from app.core.logger import logger

NSFW_MODEL = "Falconsai/nsfw_image_detection"
NSFW_THRESHOLD = 0.90
VIDEO_SAMPLE_SECONDS = 1.0
MAX_VIDEO_SAFETY_FRAMES = 300


class ContentSafetyService:

    def __init__(self):
        self.classifier = None

    def _load_classifier(self):
        if self.classifier is None:
            logger.info(
                "Loading NSFW content safety model..."
            )

            self.classifier = pipeline(
                "image-classification",
                model=NSFW_MODEL,
                device=-1
            )

            logger.info(
                "NSFW content safety model loaded"
            )

        return self.classifier

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

            classifier = self._load_classifier()
            results = classifier(
                image,
                top_k=2
            )

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
                f"unsafe={is_unsafe}"
            )

            return {
                "safe": not is_unsafe,
                "nsfw_score": nsfw_score
            }

        except Exception as e:

            logger.error(
                f"Content safety check failed: {e}")

            return {
                "safe": False,
                "nsfw_score": 1.0,
                "error": str(e)
            }

    def check_video(
        self,
        video_path: str ):

        logger.info(
            f"Running video content safety check: "
            f"{video_path}"
        )
        cap = cv2.VideoCapture(
            video_path
        )

        if not cap.isOpened():
            logger.error(
                f"Could not open video for safety scan: "
                f"{video_path}"
            )

            return {
                "safe": False,
                "reason": "Could not open video"
            }

        fps = cap.get(
            cv2.CAP_PROP_FPS )

        frame_count = cap.get(
            cv2.CAP_PROP_FRAME_COUNT)

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

        if estimated_frames > MAX_VIDEO_SAFETY_FRAMES:
            interval = (
                duration /
                MAX_VIDEO_SAFETY_FRAMES
            )

        classifier = self._load_classifier()

        current_time = 0.0
        scanned_frames = 0
        highest_score = 0.0

        try:

            while current_time < duration:
                cap.set(
                    cv2.CAP_PROP_POS_MSEC,
                    current_time * 1000 )
                success, frame = cap.read()

                if not success:
                    break

                frame_rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB  )
                
                image = Image.fromarray(
                    frame_rgb )

                results = classifier(
                    image,
                    top_k=2)

                frame_score = 0.0
                
                for result in results:
                    if (
                        result["label"]
                        .lower()
                        == "nsfw"  ):

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
                    f"Safety frame {scanned_frames}: "
                    f"time={current_time:.2f}s, "
                    f"nsfw_score={frame_score:.4f}"
                )

                if (
                    frame_score
                    >= NSFW_THRESHOLD   ):
                    logger.warning(
                        "Unsafe content detected "
                        f"in video at "
                        f"{current_time:.2f}s"
                    )

                    return {
                        "safe": False,
                        "nsfw_score": frame_score,
                        "timestamp": current_time,
                        "frames_scanned": scanned_frames
                    }

                current_time += interval
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
            "frames_scanned": scanned_frames
        }

content_safety_service = ( ContentSafetyService())