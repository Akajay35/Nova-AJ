from __future__ import annotations
from typing import Any

class MemoryContext:
    """Build a small, relevant context bundle from approved personal context."""
    def __init__(self, memory: Any, profile: Any = None, tasks: Any = None, max_items: int = 5):
        self.memory, self.profile, self.tasks = memory, profile, tasks
        self.max_items = max_items

    def relevant(self, query: str):
        try:
            return self.memory.search(query)[:self.max_items]
        except Exception:
            return []

    def build(self, query: str) -> dict:
        result = {"profile": {}, "memories": [], "tasks": []}
        if self.profile is not None:
            try: result["profile"] = self.profile.summary()
            except Exception: pass
        result["memories"] = self.relevant(query)
        if self.tasks is not None:
            try: result["tasks"] = self.tasks.list_open()[:self.max_items]
            except Exception: pass
        return result

    def build_text(self, query: str) -> str:
        context = self.build(query)
        lines = []
        for key, value in context.get("profile", {}).items():
            lines.append(f"Profile - {key}: {value}")
        for item in context.get("memories", []):
            lines.append(f"Memory - {item.get('key', '')}: {item.get('value', '')}")
        return "\n".join(lines)
