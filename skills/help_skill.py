from core.base_skill import BaseSkill

class HelpSkill(BaseSkill):
    name = "help"; description = "List installed skills"; keywords = ["help", "what can you do", "skills", "capabilities"]
    def handle(self, query: str, context=None) -> str:
        names = context["assistant"].skills.names() if context and "assistant" in context else []
        return "Installed skills: " + ", ".join(names) + ". Ask for something I cannot do and I will record a proposal for a future skill."
