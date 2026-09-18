import json
import os

class ChunkStorageService:
    CHUNKS_FILE = "storage/metadata/chunks.json"

    def __init__(self):
        os.makedirs(
            os.path.dirname(self.CHUNKS_FILE),
            exist_ok=True,
        )

    def save_chunks(
        self,
        file_id: str,
        chunks: list[dict],
    ):
        data = self._load()
        data[file_id] = chunks
        self._save(data)

    def get_chunks(
        self,
        file_id: str,
    ) -> list[dict]:
        data = self._load()

        return data.get(file_id, [])

    def get_all_chunks(self) -> list[dict]:
        data = self._load()
        chunks = []
        for file_chunks in data.values():
            chunks.extend(file_chunks)

        return chunks

    def _load(self) -> dict:
        if not os.path.exists(self.CHUNKS_FILE):
            return {}

        with open(self.CHUNKS_FILE, "r") as file:
            return json.load(file)

    def _save(self, data: dict):
        with open(self.CHUNKS_FILE, "w") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )