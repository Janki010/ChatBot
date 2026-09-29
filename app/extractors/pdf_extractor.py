import fitz

from app.extractors.base import BaseExtractor
from app.services.visual_extraction_service import VisualExtractionService


class PDFExtractor(BaseExtractor):

    def __init__(self):
        self.visual_extraction_service = (
            VisualExtractionService()
        )

    def extract(self, file_path: str) -> list[dict]:
        results = []

        document = fitz.open(file_path)

        try:
            for page_number, page in enumerate(
                document,
                start=1,
            ):
                text = page.get_text("text").strip()

                if text:
                    results.append({
                        "source_type": "page",
                        "source_number": page_number,
                        "element_type": "text",
                        "metadata": {
                            "page_number": page_number,
                        },
                        "text": text,
                    })

                if not self._has_visual_content(page):
                    continue

                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                page_image = pixmap.tobytes("png")

                visual_result = (
                    self.visual_extraction_service.extract(
                        page_image=page_image,
                    )
                )

                visual_text = visual_result.get(
                    "text",
                    "",
                ).strip()

                if visual_text:
                    results.append({
                        "source_type": "page",
                        "source_number": page_number,
                        "element_type": visual_result[
                            "element_type"
                        ],
                        "metadata": {
                            "page_number": page_number,
                            **visual_result.get(
                                "metadata",
                                {},
                            ),
                        },
                        "text": visual_text,
                    })

        finally:
            document.close()

        return results

    @staticmethod
    def _has_visual_content(page) -> bool:
        if page.get_drawings():
            return True

        return False