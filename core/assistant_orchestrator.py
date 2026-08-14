from __future__ import annotations
from dataclasses import dataclass

@dataclass
class OrchestrationResult:
    intent: str
    result: object

class AssistantOrchestrator:
    """Dispatches classified commands to application services."""
    def __init__(self, router, handlers: dict[str, object] | None = None):
        self.router = router
        self.handlers = handlers or {}

    def handle(self, text: str) -> OrchestrationResult:
        route = self.router.route(text)
        handler = self.handlers.get(route.intent)
        if handler is None:
            return OrchestrationResult(route.intent, route.response)
        result = handler(text)
        return OrchestrationResult(route.intent, result)
