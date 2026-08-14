from __future__ import annotations
from typing import Any

class MemoryContext:
    """Build a small, relevant context bundle without exposing the full memory store."""
    def __init__(self, memory: Any, profile: Any, tasks: Any = None):
        self.memory, self.profile, self.tasks = memory, profile, tasks

    def build(self, query: str) -> dict:
        result = {"profile": {}, "memories": [], "tasks": []}
        try: result["profile"] = self.profile.summary()
        except Exception: pass
        try: result["memories"] = self.memory.search(query)[:5]
        except Exception: pass
        if self.tasks is not None:
            try: result["tasks"] = self.tasks.list_open()[:5]
            except Exception: pass
        return result
