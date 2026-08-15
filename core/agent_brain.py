from __future__ import annotations

from typing import Any


class AgentBrain:
    """Provider-backed reasoning boundary for Nova's agent layer."""

    def __init__(self, provider: Any):
        self.provider = provider

    def respond(
        self,
        query: str,
        history: list[dict] | None = None,
        personal_context: dict | None = None,
    ) -> str | None:
        """Ask the configured AI provider for a response; return None if unavailable."""
        return self.provider.answer(query, history or [], personal_context or {})
