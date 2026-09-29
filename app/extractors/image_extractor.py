from PIL import Image
import pytesseract

from app.extractors.base import BaseExtractor
from app.services.visual_extraction_service import VisualExtractionService

class ImageExtractor(BaseExtractor):

    def __init__(self):
        self.visual_extraction_service = (
            VisualExtractionService()
        )

    def extract(self, file_path: str) -> list[dict]:
        results = []

        image = Image.open(file_path)

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


        with open(file_path, "rb") as image_file:
            image_bytes = image_file.read()

        visual_result = (
            self.visual_extraction_service.extract(
                page_image=image_bytes,
            )
        )

        if not visual_result.get("has_visual"):
            return results

        visual_text = visual_result.get(
            "text",
            "",
        ).strip()

        if visual_text:
            results.append({
                "source_type": "image",
                "source_number": 1,
                "element_type": visual_result[
                    "element_type"
                ],
                "metadata": {
                    "width": image.width,
                    "height": image.height,
                    **visual_result.get(
                        "metadata",
                        {},
                    ),
                },
                "text": visual_text,
            })

        return results
