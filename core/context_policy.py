from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContextPolicy:
    """Deterministic, explicit allowlist for context supplied to an AI response."""

    max_profile_fields: int = 12
    max_memories: int = 6
    max_conversations: int = 8
    max_text_chars: int = 1200
    allowed_profile_fields: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "preferred_name",
                "language",
                "timezone",
                "communication_style",
                "response_style",
                "theme",
            }
        )
    )
    allowed_item_fields: frozenset[str] = field(
        default_factory=lambda: frozenset({"text", "role", "timestamp", "topic"})
    )

    def _clip(self, value: Any) -> str:
        text = str(value)
        return text if len(text) <= self.max_text_chars else text[: self.max_text_chars].rstrip() + "…"

    def apply(self, snapshot: Any) -> dict[str, Any]:
        raw_profile = dict(getattr(snapshot, "profile", {}) or {})
        profile = {
            key: self._clip(value)
            for key, value in raw_profile.items()
            if key in self.allowed_profile_fields
        }
        if len(profile) > self.max_profile_fields:
            profile = dict(list(profile.items())[: self.max_profile_fields])

        memories = [self._normalize(item) for item in list(getattr(snapshot, "memories", []) or [])[-self.max_memories :]]
        conversations = [self._normalize(item) for item in list(getattr(snapshot, "conversations", []) or [])[-self.max_conversations :]]

        return {
            "profile": profile,
            "relevant_memories": memories,
            "relevant_conversations": conversations,
        }

    def _normalize(self, item: Any) -> dict[str, Any]:
        if not isinstance(item, dict):
            return {"text": self._clip(item)}
        return {
            key: (self._clip(value) if key in {"text", "topic"} else value)
            for key, value in item.items()
            if key in self.allowed_item_fields
        }
