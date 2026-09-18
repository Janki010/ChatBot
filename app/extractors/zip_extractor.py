import os
import tempfile
import zipfile

from app.extractors.base import BaseExtractor


class ZIPExtractor(BaseExtractor):
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".json",
        ".png",
        ".jpg",
        ".jpeg",
    }

    def extract(self, file_path: str) -> list[dict]:
        from app.extractors.extract_factory import ExtractorFactory

        results = []

        zip_filename = os.path.basename(file_path)

        with zipfile.ZipFile(file_path, "r") as archive:

            for member in archive.infolist():

                if member.is_dir():
                    continue

                extension = os.path.splitext(
                    member.filename
                )[1].lower()

                if extension not in self.SUPPORTED_EXTENSIONS:
                    continue

                file_type = extension.lstrip(".")

                actual_filename = os.path.basename(
                    member.filename
                )

                with tempfile.TemporaryDirectory() as temp_dir:
                    extracted_path = archive.extract(
                        member,
                        path=temp_dir,
                    )

                    extractor = ExtractorFactory.get(
                        file_type
                    )

                    documents = extractor.extract(
                        extracted_path
                    )

                    for document in documents:
                        document_metadata = document.get(
                            "metadata",
                            {},
                        )

                        document["metadata"] = {
                            **document_metadata,

                            # Actual file inside ZIP
                            "filename": actual_filename,
                            "file_type": file_type,

                            # ZIP origin information
                            "zip_filename": zip_filename,
                            "zip_path": member.filename,
                        }

                        results.append(document)

        return results