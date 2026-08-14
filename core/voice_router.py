from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    intent: str
    confidence: float
    text: str

class VoiceRouter:
    """Small deterministic router for common personal-assistant intents."""
    def route(self, text: str) -> Route:
        q=text.strip(); low=q.lower()
        rules=(
            ("reminder", ("remind me", "reminder", "remind")),
            ("project", ("project", "projects")),
            ("daily_plan", ("daily plan", "morning briefing", "priorities today")),
            ("memory", ("remember", "forget", "what do you remember")),
            ("skill", ("skill", "learn a skill")),
        )
        for intent, words in rules:
            if any(w in low for w in words): return Route(intent, 0.95, q)
        return Route("general", 0.50, q)
