import json
import os


class FileStorageService:
    METADATA_FILE = "storage/metadata/files.json"

    def get_file(self, file_id: str) -> dict | None:
        if not os.path.exists(self.METADATA_FILE):
            return None

        with open(self.METADATA_FILE, "r") as f:
            files = json.load(f)

        return files.get(file_id)