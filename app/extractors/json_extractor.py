import json

from app.extractors.base import BaseExtractor


class JSONExtractor(BaseExtractor):

    def extract(self, file_path: str) -> list[dict]:
        results = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self._extract_blocks(
            data=data,
            results=results,
        )

        return results

    def _extract_blocks(
        self,
        data,
        results: list[dict],
        path: str = "$",
    ):
        if isinstance(data, dict):

            # Keep a logical object together.
            if self._is_flat_object(data):
                results.append({
                    "source_type": "json",
                    "source_number": len(results) + 1,
                    "element_type": "object",
                    "metadata": {
                        "json_path": path,
                    },
                    "text": self._format_object(data),
                })
                return

            for key, value in data.items():
                self._extract_blocks(
                    data=value,
                    results=results,
                    path=f"{path}.{key}",
                )

        elif isinstance(data, list):

            for index, value in enumerate(data):
                self._extract_blocks(
                    data=value,
                    results=results,
                    path=f"{path}[{index}]",
                )

        else:
            results.append({
                "source_type": "json",
                "source_number": len(results) + 1,
                "element_type": "value",
                "metadata": {
                    "json_path": path,
                },
                "text": f"{path}: {self._format_value(data)}",
            })

    @staticmethod
    def _is_flat_object(data: dict) -> bool:
        return all(
            not isinstance(value, (dict, list))
            for value in data.values()
        )

    @staticmethod
    def _format_object(data: dict) -> str:
        return "\n".join(
            f"{key}: {JSONExtractor._format_value(value)}"
            for key, value in data.items()
        )

    @staticmethod
    def _format_value(value) -> str:
        if value is None:
            return "null"

        if isinstance(value, bool):
            return str(value).lower()

        return str(value)