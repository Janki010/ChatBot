from app.extractors.base import BaseExtractor

class TXTExtractor(BaseExtractor):
    def extract(self, file_path: str) -> list[dict]:
        results = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            lines = file.readlines()

        text = "".join(lines).strip()

        if not text:
            return results

        results.append({
            "source_type": "text",
            "source_number": 1,
            "element_type": "text",
            "metadata": {
                "start_line": 1,
                "end_line": len(lines),
            },
            "text": text,
        })

        return results