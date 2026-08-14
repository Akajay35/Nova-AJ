from core.base_skill import BaseSkill

class SystemSkill(BaseSkill):
    name = "system"; description = "Assistant status"; keywords = ["status", "are you ready", "system status"]
    def handle(self, query: str, context=None) -> str:
        assistant = context.get("assistant") if context else None
        count = len(assistant.skills.skills) if assistant else 0
        return f"Nova AJ is online with {count} installed skills and local memory enabled."
