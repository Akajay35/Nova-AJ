from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .conversation_history import ConversationHistory
from .memory import MemoryStore
from .profile import ProfileStore


@dataclass(frozen=True)
class ContextSnapshot:
    profile: dict[str, Any]
    memories: list[dict[str, Any]]
    conversations: list[dict[str, Any]]


class ContextIntelligence:
    """Build a deterministic personal-context view without mixing data stores."""

    STOP_WORDS = {
        "about", "and", "can", "did", "do", "for", "from", "have", "i", "in",
        "is", "me", "my", "of", "please", "recent", "the", "to", "we", "what",
        "with", "you", "yesterday", "today",
    }

    def __init__(self, profile: ProfileStore, memory: MemoryStore, history: ConversationHistory) -> None:
        self.profile = profile
        self.memory = memory
        self.history = history

    @classmethod
    def _terms(cls, query: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9_]+", query.lower())
            if token not in cls.STOP_WORDS and len(token) > 1
        }

    def snapshot(self, query: str = "", *, memory_limit: int = 6, history_limit: int = 8) -> ContextSnapshot:
        cleaned = query.strip()
        terms = self._terms(cleaned)
        memories = self.memory.recent(memory_limit)
        conversations = self.history.recent(history_limit)

        if terms:
            memory_matches = [
                item for item in self.memory.all()
                if terms & self._terms(str(item.get("text", "")))
            ]
            if memory_matches:
                memories = memory_matches[-max(1, memory_limit):]

            history_matches = [
                item for item in self.history.all()
                if terms & self._terms(str(item.get("text", "")))
            ]
            if history_matches:
                conversations = history_matches[-max(1, history_limit):]

        return ContextSnapshot(
            profile=self.profile.summary(),
            memories=memories,
            conversations=conversations,
        )

    def render(self, query: str = "") -> str:
        snapshot = self.snapshot(query)
        return str({
            "profile": snapshot.profile,
            "relevant_memories": snapshot.memories,
            "relevant_conversations": snapshot.conversations,
        })
