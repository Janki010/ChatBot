import re

from app.extractors.base import BaseExtractor

class MDExtractor(BaseExtractor):
    def extract(self, file_path: str) -> list[dict]:
        results = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read()

        if not content.strip():
            return results

        lines = content.splitlines()

        current_heading = None
        current_start_line = 1
        current_content = []

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            heading_match = re.match(
                r"^(#{1,6})\s+(.+?)\s*$",
                line,
            )

            if heading_match:
                # Save previous section
                if current_content:
                    text = "\n".join(
                        current_content
                    ).strip()

                    if text:
                        results.append({
                            "source_type": "section",
                            "source_number": len(results) + 1,
                            "element_type": "text",
                            "metadata": {
                                "heading": current_heading,
                                "start_line": current_start_line,
                                "end_line": line_number - 1,
                            },
                            "text": text,
                        })

                current_heading = heading_match.group(2)
                current_start_line = line_number

                current_content = [line]

            else:
                current_content.append(line)

        if current_content:
            text = "\n".join(
                current_content
            ).strip()

            if text:
                results.append({
                    "source_type": "section",
                    "source_number": len(results) + 1,
                    "element_type": "text",
                    "metadata": {
                        "heading": current_heading,
                        "start_line": current_start_line,
                        "end_line": len(lines),
                    },
                    "text": text,
                })

        return results