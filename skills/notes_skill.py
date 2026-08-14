from core.base_skill import BaseSkill

class NotesSkill(BaseSkill):
    name = "notes"; description = "Save and read personal notes"; keywords = ["note", "remember", "remind me", "save this"]
    def handle(self, query: str, context=None) -> str:
        memory = context["memory"] if context else None
        text = query
        for prefix in ["remember", "take a note", "note", "save this", "remind me"]:
            if text.lower().startswith(prefix): text = text[len(prefix):].lstrip(" :,-")
        if not text: return "What would you like me to remember?"
        if memory: memory.remember(text, "note")
        return "Got it. I saved that in local memory."
