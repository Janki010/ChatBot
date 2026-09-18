import json
import os
import shutil
import uuid

from fastapi import UploadFile


class UploadFileService:

    UPLOAD_DIR = "storage/uploads"
    METADATA_FILE = "storage/metadata/files.json"

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(
            os.path.dirname(self.METADATA_FILE),
            exist_ok=True,
        )

    def upload_file(self, file: UploadFile):
        file_id = str(uuid.uuid4())
        extension = os.path.splitext(file.filename)[1].lower()

        file_dir = os.path.join(
            self.UPLOAD_DIR,
            file_id,
        )
        os.makedirs(file_dir, exist_ok=True)

        filename = os.path.basename(file.filename)

        file_path = os.path.join(
            file_dir,
            filename,
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        metadata = {
            "filename": filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "file_type": extension.lstrip("."),
        }

        self._save_metadata(file_id, metadata)

        return file_id

    def _save_metadata(self, file_id: str, metadata: dict):
        data = {}
        if os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "r") as f:
                data = json.load(f)
        data[file_id] = metadata
        with open(self.METADATA_FILE, "w") as f:
            json.dump(data, f, indent=4)