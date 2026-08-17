from __future__ import annotations

import re
from dataclasses import dataclass

from .context_intelligence import ContextIntelligence
from .conversation import ConversationContext


@dataclass(frozen=True)
class ResolvedContext:
    query: str
    subject: str | None
    source: str
    confidence: float = 0.0


class ContextResolver:
    """Conservative resolver with source-aware personal-context minimization."""

    REFERENCE_RE = re.compile(r"\b(he|she|they|them|his|her|their|it|that person|that project|that goal)\b", re.I)
    MEMORY_HINTS = ("remember", "memory", "saved", "what did i tell you")
    HISTORY_HINTS = ("discuss", "discussed", "conversation", "chat", "yesterday", "today", "recent")
    PROFILE_HINTS = ("my preference", "my goal", "my project", "my note", "what is my")

    def __init__(self, conversation: ConversationContext, intelligence: ContextIntelligence) -> None:
        self.conversation = conversation
        self.intelligence = intelligence

    @staticmethod
    def _has_hint(text: str, hints: tuple[str, ...]) -> bool:
        return any(re.search(rf"\b{re.escape(hint)}\b", text) for hint in hints)

    def resolve(self, text: str) -> ResolvedContext:
        cleaned = text.strip()
        if not cleaned:
            return ResolvedContext("", None, "none", 0.0)

        if self.REFERENCE_RE.search(cleaned) and self.conversation.last_subject:
            resolved = self.conversation.resolve(cleaned)
            return ResolvedContext(resolved, self.conversation.last_subject, "conversation", 1.0)

        lowered = cleaned.lower()
        if self._has_hint(lowered, self.PROFILE_HINTS):
            return ResolvedContext(cleaned, None, "profile", 0.95)
        if self._has_hint(lowered, self.MEMORY_HINTS):
            return ResolvedContext(cleaned, None, "memory", 0.95)
        if self._has_hint(lowered, self.HISTORY_HINTS):
            return ResolvedContext(cleaned, None, "history", 0.95)
        return ResolvedContext(cleaned, None, "none", 0.0)

    def context_for(self, text: str) -> dict:
        resolved = self.resolve(text)
        if resolved.confidence == 0.0:
            return {
                "source": "none",
                "confidence": 0.0,
                "subject": None,
                "profile": {},
                "relevant_memories": [],
                "relevant_conversations": [],
            }

        snapshot = self.intelligence.snapshot(resolved.query)
        return {
            "source": resolved.source,
            "confidence": resolved.confidence,
            "subject": resolved.subject,
            "profile": snapshot.profile if resolved.source == "profile" else {},
            "relevant_memories": snapshot.memories if resolved.source in {"memory", "conversation"} else [],
            "relevant_conversations": snapshot.conversations if resolved.source in {"history", "conversation"} else [],
        }
