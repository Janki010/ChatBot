import json
import traceback
from typing import Tuple, List, Dict, Any

import requests


class AIService:
    def call_llm_service(
            self,
            messages: List[Dict[str, str]],
    ) -> Tuple[Any, Dict]:

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}",
        }

        payload = {"model": self.openai_model, "input": messages, "temperature": 0}

        try:
            response = requests.post(
                self.openai_api_url, headers=headers, json=payload, timeout=240
            )

            response.raise_for_status()

            response_data = response.json()
            response_content = response_data['choices'][0]['message']['content']
            parsed_result = json.loads(response_content)


            return parsed_result

        except Exception as e:
            print(f"retrying.........")
            print(f"Unexpected error in LLM service call: {str(e)}")
            print(traceback.format_exc())
            raise