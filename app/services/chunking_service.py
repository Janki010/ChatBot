import uuid


class ChunkingService:

    def chunk_documents(
        self,
        documents: list[dict],
        file_id: str,
        metadata: dict,
    ) -> list[dict]:
        chunks = []

        for document in documents:
            text = document.get("text", "").strip()

            if not text:
                continue

            source_type = document.get(
                "source_type"
            )

            source_number = document.get(
                "source_number"
            )

            document_metadata = document.get(
                "metadata",
                {}
            )

            filename = document_metadata.get(
                "filename",
                metadata.get("filename"),
            )

            file_type = document_metadata.get(
                "file_type",
                metadata.get("file_type"),
            )

            text_chunks = self._split_text(text)

            for chunk_text in text_chunks:

                chunk = {
                    "chunk_id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "filename": filename,
                    "file_type": file_type,
                    "source_type": source_type,
                    "source_number": source_number,
                    "text": chunk_text,
                }

                # Preserve ZIP information if available.
                if document_metadata.get("zip_filename"):
                    chunk["zip_filename"] = (
                        document_metadata["zip_filename"]
                    )

                if document_metadata.get("zip_path"):
                    chunk["zip_path"] = (
                        document_metadata["zip_path"]
                    )

                chunks.append(chunk)

        return chunks

    def _split_text(
        self,
        text: str,
        max_chars: int = 1500,
    ) -> list[str]:

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:

            # If a single paragraph itself is larger
            # than max_chars, split it directly.
            if len(paragraph) > max_chars:

                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                chunks.extend(
                    self._split_large_text(
                        paragraph,
                        max_chars,
                    )
                )

                continue

            if (
                len(current_chunk) + len(paragraph)
                > max_chars
            ):
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = paragraph

            else:
                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def _split_large_text(
        text: str,
        max_chars: int,
    ) -> list[str]:
        return [
            text[index:index + max_chars]
            for index in range(
                0,
                len(text),
                max_chars,
            )
        ]