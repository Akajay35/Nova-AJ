from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

from .voice_router import VoiceRouter, Route

@dataclass
class OrchestratorResult:
    response: str
    route: Route
    handler: str

class NovaOrchestrator:
    """Single, deterministic entry point for text/voice requests.

    Domain handlers are injected by the application. The orchestrator does not
    execute arbitrary code and falls back to the configured general handler.
    """
    def __init__(self, *, router: VoiceRouter | None = None,
                 handlers: dict[str, Callable[[str], str]] | None = None,
                 general_handler: Callable[[str], str] | None = None) -> None:
        self.router = router or VoiceRouter()
        self.handlers = handlers or {}
        self.general_handler = general_handler or (lambda text: "I can help with that.")

    def handle(self, text: str) -> OrchestratorResult:
        route = self.router.route(text)
        handler = self.handlers.get(route.intent)
        if handler is None:
            return OrchestratorResult(self.general_handler(route.text), route, "general")
        try:
            return OrchestratorResult(str(handler(route.text)), route, route.intent)
        except Exception:
            return OrchestratorResult("That action could not be completed safely.", route, route.intent)
