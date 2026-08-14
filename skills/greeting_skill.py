from core.base_skill import BaseSkill

class GreetingSkill(BaseSkill):
    name = "greeting"; description = "Greetings and assistant status"; keywords = ["hello", "hi", "hey", "how are you", "good morning", "good evening"]
    def handle(self, query: str, context=None) -> str:
        return "Hello! I'm Nova AJ, your personal AI assistant. I'm ready to help."
