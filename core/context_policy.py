from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextPolicy:
    """Deterministic limits for context supplied to an AI response."""

    max_profile_fields: int = 12
    max_memories: int = 6
    max_conversations: int = 8
    max_text_chars: int = 1200

    def _clip(self, value: Any) -> str:
        text = str(value)
        return text if len(text) <= self.max_text_chars else text[: self.max_text_chars].rstrip() + "…"

    def apply(self, snapshot: Any) -> dict[str, Any]:
        profile = dict(getattr(snapshot, "profile", {}) or {})
        if len(profile) > self.max_profile_fields:
            profile = dict(list(profile.items())[: self.max_profile_fields])

        memories = []
        for item in list(getattr(snapshot, "memories", []) or [])[-self.max_memories :]:
            memories.append(self._normalize(item))

        conversations = []
        for item in list(getattr(snapshot, "conversations", []) or [])[-self.max_conversations :]:
            conversations.append(self._normalize(item))

        return {
            "profile": profile,
            "relevant_memories": memories,
            "relevant_conversations": conversations,
        }

    def _normalize(self, item: Any) -> dict[str, Any]:
        if not isinstance(item, dict):
            return {"text": self._clip(item)}
        result = dict(item)
        if "text" in result:
            result["text"] = self._clip(result["text"])
        return result
