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


class ContextResolver:
    """Conservative resolver for follow-up references and personal-context queries."""

    REFERENCE_RE = re.compile(r"\b(he|she|they|them|his|her|their|it|that person|that project|that goal)\b", re.I)
    MEMORY_HINTS = ("remember", "memory", "saved", "what did i tell you")
    HISTORY_HINTS = ("discuss", "discussed", "conversation", "chat", "yesterday", "today", "recent")
    PROFILE_HINTS = ("my preference", "my goal", "my project", "my note", "what is my")

    def __init__(self, conversation: ConversationContext, intelligence: ContextIntelligence) -> None:
        self.conversation = conversation
        self.intelligence = intelligence

    def resolve(self, text: str) -> ResolvedContext:
        cleaned = text.strip()
        if not cleaned:
            return ResolvedContext("", None, "none")

        if self.REFERENCE_RE.search(cleaned) and self.conversation.last_subject:
            resolved = self.conversation.resolve(cleaned)
            return ResolvedContext(resolved, self.conversation.last_subject, "conversation")

        lowered = cleaned.lower()
        if any(hint in lowered for hint in self.PROFILE_HINTS):
            return ResolvedContext(cleaned, None, "profile")
        if any(hint in lowered for hint in self.MEMORY_HINTS):
            return ResolvedContext(cleaned, None, "memory")
        if any(hint in lowered for hint in self.HISTORY_HINTS):
            return ResolvedContext(cleaned, None, "history")
        return ResolvedContext(cleaned, None, "none")

    def context_for(self, text: str) -> dict:
        resolved = self.resolve(text)
        snapshot = self.intelligence.snapshot(resolved.query)
        return {
            "source": resolved.source,
            "subject": resolved.subject,
            "profile": snapshot.profile,
            "relevant_memories": snapshot.memories,
            "relevant_conversations": snapshot.conversations,
        }
