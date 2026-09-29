import base64
import json
import logging
import os
from dotenv import load_dotenv
import requests

from app.config.prompts.extract_visual_elements import ExtractVisualElements

logger = logging.getLogger(__name__)

load_dotenv()

class VisualExtractionService:

    SUPPORTED_TYPES = {
        "table",
        "chart",
        "other_visual_element",
    }

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_url = os.getenv("OPENAI_API_URL")
        self.openai_model = os.getenv("OPENAI_MODEL")

        self.extract_visual_element_prompt = ExtractVisualElements()

    def extract(self, page_image: bytes) -> dict:
        image_base64 = base64.b64encode(page_image).decode("utf-8")

        prompt = (
            self.extract_visual_element_prompt
            .Extract_Visual_Elements
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/png;base64,{image_base64}"
                        ),
                    },
                ],
            }
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}",
        }

        payload = {
            "model": self.openai_model,
            "input": messages,
            "temperature": 0,
            "text": {
                "format": {
                    "type": "json_object"
                }
            },
        }

        response = requests.post(
            self.openai_api_url,
            headers=headers,
            json=payload,
            timeout=240,
        )

        response.raise_for_status()

        data = response.json()

        content = data["output"][0]["content"][0]["text"]
        result = json.loads(content)

        element_type = result.get("element_type")

        if element_type not in self.SUPPORTED_TYPES:
            logger.warning(
                "Invalid visual element type returned: %s",
                element_type,
            )

            result["element_type"] = "other_visual_element"

        return result