from pathlib import Path

from fastapi import UploadFile


class FileValidator:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".csv",
        ".json",
        ".txt",
        ".md",
        ".png",
        ".jpg",
        ".jpeg",
        ".zip"
    }

    @classmethod
    def validate_file(cls, file: UploadFile):
        errors = []

        if not file.filename:
            errors.append("Filename is required.")
            return errors

        extension = Path(file.filename).suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            errors.append(
                f"Unsupported file type: {extension}"
            )

        return errors