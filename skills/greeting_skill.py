import random

from core.base_skill import BaseSkill
import config


class GreetingSkill(BaseSkill):
    name = "greeting"
    keywords = ["hello", "hi", "hey", "how are you", "good morning", "good evening"]

    responses = [
        f"Hey, I'm {config.FULL_NAME}. What can I help with?",
        "Hi there! What do you need?",
        "I'm doing great, thanks for asking. What's up?",
    ]

    def handle(self, query: str) -> str:
        return random.choice(self.responses)
