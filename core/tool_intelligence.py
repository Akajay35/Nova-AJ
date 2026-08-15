from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .tool_registry import ToolRegistry


@dataclass(frozen=True)
class ToolMatch:
    name: str | None
    arguments: dict[str, Any]
    score: int = 0


class ToolIntelligence:
    """Conservative natural-language selector for registered tools."""

    STOP_WORDS = {
        "a", "an", "and", "are", "can", "do", "for", "have", "i", "in",
        "is", "me", "my", "of", "please", "show", "the", "to", "what", "you",
    }

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-z0-9_]+", text.lower())
            if token not in cls.STOP_WORDS and len(token) > 1
        }

    def match(self, query: str) -> ToolMatch:
        text = query.strip()
        lowered = text.lower()
        if not text:
            return ToolMatch(None, {})

        # Argument extraction is explicit for user-value tools; arbitrary
        # function arguments are never guessed.
        for prefix in ("remember that ", "remember ", "save this: "):
            if lowered.startswith(prefix) and self.tools.get("remember"):
                value = text[len(prefix):].strip()
                if value:
                    return ToolMatch("remember", {"text": value}, 100)

        for prefix in ("search my memory for ", "search memory for ", "find in memory "):
            if lowered.startswith(prefix) and self.tools.get("search_memory"):
                value = text[len(prefix):].strip()
                if value:
                    return ToolMatch("search_memory", {"term": value}, 100)

        if lowered.startswith("use "):
            parts = text[4:].split(maxsplit=1)
            if parts and self.tools.get(parts[0]):
                return ToolMatch(parts[0], {"text": parts[1]} if len(parts) == 2 else {}, 100)

        query_tokens = self._tokens(text)
        candidates: list[ToolMatch] = []
        for tool in self.tools.describe():
            name_tokens = self._tokens(tool["name"].replace("_", " "))
            desc_tokens = self._tokens(tool["description"])
            overlap = query_tokens & (name_tokens | desc_tokens)
            name_overlap = query_tokens & name_tokens
            score = len(overlap) + (2 * len(name_overlap))
            if score:
                candidates.append(ToolMatch(tool["name"], {}, score))

        if not candidates:
            return ToolMatch(None, {})
        candidates.sort(key=lambda item: (item.score, item.name or ""), reverse=True)
        best = candidates[0]
        if best.score < 2 or (len(candidates) > 1 and candidates[1].score == best.score):
            return ToolMatch(None, {})
        return best
