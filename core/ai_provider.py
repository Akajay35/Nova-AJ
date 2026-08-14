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

    def answer(self, prompt: str, context: list[dict] | None = None) -> str | None:
        if not self.client:
            return None
        history = context or []
        transcript = "\n".join(f"{m['role']}: {m['text']}" for m in history[-8:])
        instructions = os.getenv(
            "NOVA_INSTRUCTIONS",
            "You are Nova AJ, a concise, friendly personal voice assistant. Answer naturally. "
            "Never claim you performed an action unless a skill actually performed it. "
            "Ask for confirmation before consequential actions."
        )
        try:
            response = self.client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                instructions=instructions,
                input=f"Recent conversation:\n{transcript}\n\nUser: {prompt}",
            )
            text = response.output_text.strip()
            return text or None
        except Exception:
            return None
