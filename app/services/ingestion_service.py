from app.extractors.extract_factory import ExtractorFactory
from app.services.bm25_service import BM25Service
from app.services.chunk_storage_service import ChunkStorageService
from app.services.chunking_service import ChunkingService
from app.services.file_storage_service import FileStorageService


class IngestionService:

    def __init__(
        self,
        bm25_service: BM25Service | None = None,
    ):
        self.file_storage_service = FileStorageService()
        self.chunking_service = ChunkingService()
        self.chunk_storage_service = ChunkStorageService()
        self.bm25_service = bm25_service

    def ingest_file(self, file_id: str):
        metadata = self.file_storage_service.get_file(
            file_id
        )

        if not metadata:
            raise FileNotFoundError(
                f"File not found: {file_id}"
            )

        extractor = ExtractorFactory.get(
            metadata["file_type"]
        )

        documents = extractor.extract(
            metadata["file_path"]
        )

        chunks = self.chunking_service.chunk_documents(
            documents=documents,
            file_id=file_id,
            metadata=metadata,
        )

        self.chunk_storage_service.save_chunks(
            file_id=file_id,
            chunks=chunks,
        )

        return {
            "file_id": file_id,
            "filename": metadata["filename"],
            "file_type": metadata["file_type"],
            "chunks_count": len(chunks),
        }

    def build_index(self):
        if self.bm25_service is None:
            raise RuntimeError(
                "BM25Service is required to build the index"
            )

        chunks = self.chunk_storage_service.get_all_chunks()

        self.bm25_service.build_index(chunks)

        file_ids = {
            chunk["file_id"]
            for chunk in chunks
        }

        return {
            "files_count": len(file_ids),
            "chunks_count": len(chunks),
        }