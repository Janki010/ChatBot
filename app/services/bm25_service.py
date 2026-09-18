from rank_bm25 import BM25Okapi


class BM25Service:

    def __init__(self):
        self.bm25 = None
        self.chunks: list[dict] = []

    def build_index(self, chunks: list[dict]) -> None:
        self.chunks = list(chunks)

        if not self.chunks:
            self.bm25 = None
            return

        tokenized_documents = [
            self._tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        self.chunks.extend(chunks)

        self.rebuild_index()

    def rebuild_index(self) -> None:
        self.build_index(self.chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        if self.bm25 is None:
            return []

        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indexes:
            chunk = self.chunks[index].copy()
            chunk["score"] = float(scores[index])
            results.append(chunk)

        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split()