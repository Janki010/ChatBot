from app.services.bm25_service import BM25Service


class AskService:
    def __init__(self, bm25_service: BM25Service):
        self.bm25_service = bm25_service

    def ask(self, query: str):
        chunks = self.bm25_service.search(
            query=query,
            top_k=2,
        )

        return chunks