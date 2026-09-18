import fitz

from app.extractors.base import BaseExtractor


class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str) -> list[dict]:
        results = []

        document = fitz.open(file_path)

        try:
            for page_number, page in enumerate(document, start=1):

                # Extract normal text
                text = page.get_text("text").strip()

                if text:
                    results.append({
                        "source_type": "page",
                        "source_number": page_number,
                        "element_type": "text",
                        "metadata": {
                            "page_number": page_number,
                        },
                        "text": text,
                    })

                # Extract tables
                tables = self._extract_tables(page)

                for table_number, table_text in enumerate(
                    tables,
                    start=1,
                ):
                    if not table_text:
                        continue

                    results.append({
                        "source_type": "page",
                        "source_number": page_number,
                        "element_type": "table",
                        "metadata": {
                            "page_number": page_number,
                            "table_number": table_number,
                        },
                        "text": table_text,
                    })

        finally:
            document.close()

        return results

    @staticmethod
    def _extract_tables(page) -> list[str]:
        tables = []

        try:
            table_finder = page.find_tables()
        except Exception:
            return tables

        for table in table_finder.tables:
            rows = table.extract()

            if not rows:
                continue

            table_text = "\n".join(
                " | ".join(
                    str(cell).strip() if cell is not None else ""
                    for cell in row
                )
                for row in rows
            ).strip()

            if table_text:
                tables.append(table_text)

        return tables