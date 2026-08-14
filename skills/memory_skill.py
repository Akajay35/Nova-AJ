from core.base_skill import BaseSkill

class MemorySkill(BaseSkill):
    name = "memory"; description = "Read saved memory"; keywords = ["show memory", "my memory", "what do you remember", "recall"]
    def handle(self, query: str, context=None) -> str:
        memory = context["memory"] if context else None
        items = memory.recent(8) if memory else []
        if not items: return "My local memory is empty."
        return "Recent memory: " + " | ".join(item["text"] for item in items)
