from core.base_skill import BaseSkill
from core.personal_context import PersonalContext

class ContextSkill(BaseSkill):
    name = "personal_context"
    description = "Remember, retrieve, and manage approved personal context."

    def __init__(self): self.context = PersonalContext()

    def matches(self, query: str) -> bool:
        q = query.lower()
        return any(x in q for x in ("remember", "what do you know", "what do you remember", "my preference", "forget this"))

    def run(self, query: str) -> str:
        q = query.strip()
        lower = q.lower()
        if lower.startswith("remember "):
            text = q[9:].strip(); self.context.remember_event(text)
            return "I'll remember that in Nova AJ's local context."
        if "what do you remember" in lower or "what do you know" in lower:
            events = self.context.snapshot().get("events", [])[-10:]
            if not events: return "I don't have any saved personal context yet."
            return "Recent context: " + " | ".join(e["text"] for e in events)
        return "I can save approved context and retrieve recent saved information."
