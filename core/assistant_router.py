from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class RouteResult:
    intent: str
    response: object

class AssistantRouter:
    """Small deterministic command router; handlers can be replaced by the real agent/skills layer."""
    def __init__(self, handlers: dict[str, Callable[[str], object]] | None = None):
        self.handlers = handlers or {}

    def classify(self, text: str) -> str:
        value=text.lower().strip()
        if value.startswith(("remind me", "reminder", "add task", "create task")): return "task"
        if value.startswith(("remember", "forget", "what do you remember")): return "memory"
        if value.startswith(("open ", "search ", "run ", "use ")): return "skill"
        return "chat"

    def route(self, text: str) -> RouteResult:
        intent=self.classify(text)
        handler=self.handlers.get(intent)
        response=handler(text) if handler else text
        return RouteResult(intent, response)
