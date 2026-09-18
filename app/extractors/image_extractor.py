from PIL import Image
import pytesseract

from app.extractors.base import BaseExtractor


class ImageExtractor(BaseExtractor):

    def extract(self, file_path: str) -> list[dict]:
        image = Image.open(file_path)

        results = []

        # 1. Extract text using OCR
        text = pytesseract.image_to_string(image).strip()

        if text:
            results.append({
                "source_type": "image",
                "source_number": 1,
                "element_type": "text",
                "metadata": {
                    "width": image.width,
                    "height": image.height,
                },
                "text": text,
            })

        # 2. Keep image as a visual source
        results.append({
            "source_type": "image",
            "source_number": 1,
            "element_type": "visual",
            "metadata": {
                "width": image.width,
                "height": image.height,
            },
            "text": "",
        })

        return results