from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class RouteResult:
    intent: str
    response: object

class AssistantRouter:
    """Routes commands and can delegate unmatched capability requests to skill learning."""
    def __init__(self, handlers: dict[str, Callable[[str], object]] | None = None, learning_loop=None):
        self.handlers = handlers or {}
        self.learning_loop = learning_loop

    def classify(self, text: str) -> str:
        value=text.lower().strip()
        if value.startswith(("remind me", "reminder", "add task", "create task")): return "task"
        if value.startswith(("remember", "forget", "what do you remember")): return "memory"
        if value.startswith(("open ", "search ", "run ", "use ")): return "skill"
        return "chat"

    def route(self, text: str) -> RouteResult:
        intent=self.classify(text)
        handler=self.handlers.get(intent)
        if handler:
            return RouteResult(intent, handler(text))
        if self.learning_loop is not None and intent == "chat":
            return RouteResult("learning", self.learning_loop.handle_capability_gap(
                text, "new_capability", "Capability requested by the user", "No existing skill matched the request"
            ))
        return RouteResult(intent, text)
