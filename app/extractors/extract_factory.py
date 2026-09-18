from app.extractors.csv_extractor import CSVExtractor
from app.extractors.docx_extractor import DOCXExtractor
from app.extractors.image_extractor import ImageExtractor
from app.extractors.json_extractor import JSONExtractor
from app.extractors.md_extractor import MDExtractor
from app.extractors.pdf_extractor import PDFExtractor
from app.extractors.pptx_extractor import PPTXExtractor
from app.extractors.txt_extractor import TXTExtractor
from app.extractors.xlsx_extractor import XLSXExtractor
from app.extractors.zip_extractor import ZIPExtractor


class ExtractorFactory:
    _extractors = {
        "pdf": PDFExtractor,
        "doc": DOCXExtractor,
        "docx": DOCXExtractor,
        "ppt": PPTXExtractor,
        "pptx": PPTXExtractor,
        "xls": XLSXExtractor,
        "xlsx": XLSXExtractor,
        "png": ImageExtractor,
        "jpg": ImageExtractor,
        "jpeg": ImageExtractor,
        "zip": ZIPExtractor,
        "csv": CSVExtractor,
        "md": MDExtractor,
        "txt": TXTExtractor,
        "json": JSONExtractor
    }

    @classmethod
    def get(cls, file_type: str):
        extractor_class = cls._extractors.get(file_type)

        if not extractor_class:
            raise ValueError(
                f"Unsupported file type: {file_type}"
            )

        return extractor_class()