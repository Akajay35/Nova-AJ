from __future__ import annotations
import os

class AIProvider:
    def __init__(self):
        self.client = None
        key = os.getenv("OPENAI_API_KEY")
        if key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=key)
            except Exception:
                self.client = None

    def answer(self, prompt: str) -> str | None:
        if not self.client: return None
        try:
            response = self.client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-5-mini"), input=prompt)
            return response.output_text.strip()
        except Exception:
            return None
