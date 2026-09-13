import os
import shutil
import pytesseract
from PIL import Image
from app.core.logger import logger


if os.name == "nt":
    windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(windows_tesseract):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract
    else:
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

else:
    tesseract_path = shutil.which("tesseract")

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        logger.warning("Tesseract executable not found in PATH")


class OCRService:

    def extract_text(self, image_path: str):
        logger.info(f"Running OCR: {image_path}")

        try:
            image = Image.open(image_path)

            text = pytesseract.image_to_string(
                image,
                lang="eng"
            )

            text = text.strip()
            logger.info(f"OCR extracted {len(text)} characters")

            return text

        except Exception as e:
            logger.error(f"OCR failed: {e}")

            return ""


ocr_service = OCRService()