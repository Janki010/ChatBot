import csv

from app.extractors.base import BaseExtractor

class CSVExtractor(BaseExtractor):
    def extract(self, file_path: str) -> list[dict]:
        results = []

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.reader(file)

            rows = list(reader)

        if not rows:
            return results

        headers = rows[0]

        data_rows = rows[1:]

        text = self._rows_to_text(
            headers=headers,
            rows=data_rows,
        )

        if not text:
            return results

        results.append({
            "source_type": "csv",
            "source_number": 1,
            "element_type": "table",
            "metadata": {
                "headers": headers,
                "row_count": len(data_rows),
                "column_count": len(headers),
            },
            "text": text,
        })

        return results

    @staticmethod
    def _rows_to_text(
        headers: list[str],
        rows: list[list[str]],
    ) -> str:
        result = []

        if headers:
            result.append(
                " | ".join(
                    value.strip()
                    for value in headers
                )
            )

        for row in rows:
            if not any(
                value.strip()
                for value in row
            ):
                continue

            result.append(
                " | ".join(
                    value.strip()
                    for value in row
                )
            )

        return "\n".join(result).strip()