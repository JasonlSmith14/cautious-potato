import json
import re
from google import genai


class Gemini:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, contents: str, model: str = "gemini-2.0-flash"):
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
        )

        return response.text

    @staticmethod
    def clean_and_parse_model_output(raw_output: str):
        cleaned = re.sub(r"^```json\s*", "", raw_output.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)
