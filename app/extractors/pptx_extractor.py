import os
import subprocess
import tempfile

from app.extractors.base import BaseExtractor
from app.extractors.pdf_extractor import PDFExtractor
from app.services.visual_extraction_service import VisualExtractionService


class PPTXExtractor(BaseExtractor):
    def __init__(
            self
    ):
        self.visual_extraction_service = VisualExtractionService()
        self.pdf_extractor = PDFExtractor()

    def extract(self, file_path: str) -> list[dict]:
        pdf_path = self._convert(
            file_path
        )

        result = self.pdf_extractor.extract(pdf_path)

        return result


    @staticmethod
    def _convert(file_path: str) -> str:
        output_dir = tempfile.mkdtemp()

        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                file_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        filename = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        pdf_path = os.path.join(
            output_dir,
            f"{filename}.pdf",
        )

        if not os.path.exists(pdf_path):
            raise RuntimeError(
                f"Failed to convert PPTX to PDF: {file_path}"
            )

        return pdf_path