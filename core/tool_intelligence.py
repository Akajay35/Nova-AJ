from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .tool_registry import ToolRegistry


@dataclass(frozen=True)
class ToolMatch:
    tool_name: str | None
    arguments: dict[str, Any]
    score: int = 0


class ToolIntelligence:
    """Conservative natural-language tool selection and argument extraction.

    Selection is deterministic: only registered tools can be returned, and a
    match must clear a confidence threshold. This keeps the intelligence layer
    useful without allowing arbitrary model-generated tool names or code.
    """

    _SYNONYMS = {
        "show": {"show", "display", "view", "tell", "give", "what"},
        "list": {"list", "show", "display", "available", "what"},
        "profile": {"profile", "details", "information", "info"},
        "memory": {"memory", "memories", "remember", "recall"},
        "skill": {"skill", "skills"},
        "system": {"system", "status", "health", "readiness"},
        "diagnostic": {"diagnostic", "diagnostics", "debug", "startup"},
        "refresh": {"refresh", "reload", "update"},
        "tool": {"tool", "tools", "capability", "capabilities"},
    }

    def __init__(self, tools: ToolRegistry, threshold: int = 2) -> None:
        self.tools = tools
        self.threshold = threshold

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9_]+", text.lower()))

    def _expanded(self, tokens: set[str]) -> set[str]:
        expanded = set(tokens)
        for canonical, values in self._SYNONYMS.items():
            if tokens & values:
                expanded.add(canonical)
        return expanded

    def _special_match(self, text: str) -> ToolMatch | None:
        lowered = text.lower().strip()

        patterns = (
            (r"^(?:remember that|remember|save this:)\s+(.+)$", "remember", "text"),
            (r"^(?:search my memory for|search memory for|find in memory)\s+(.+)$", "search_memory", "term"),
            (r"^(?:forget memory|delete memory|forget)\s+(.+)$", "forget", "value"),
        )
        for pattern, kind, argument in patterns:
            match = re.match(pattern, text.strip(), re.IGNORECASE)
            if not match:
                continue
            value = match.group(1).strip()
            if not value:
                return ToolMatch(None, {})
            if kind == "remember":
                return ToolMatch("remember", {"text": value}, 100)
            if kind == "search_memory":
                return ToolMatch("search_memory", {"term": value}, 100)
            if kind == "forget":
                if re.fullmatch(r"[0-9a-f]{8,64}", value, re.IGNORECASE):
                    return ToolMatch("forget_memory", {"memory_id": value}, 100)
                return ToolMatch("forget_matching_memory", {"term": value}, 100)

        return None

    def match(self, query: str) -> ToolMatch:
        text = query.strip()
        if not text:
            return ToolMatch(None, {})

        special = self._special_match(text)
        if special is not None and self.tools.get(special.tool_name or ""):
            return special

        lowered = text.lower()
        if lowered.startswith("use "):
            parts = text[4:].split(maxsplit=1)
            if parts and self.tools.get(parts[0]):
                return ToolMatch(parts[0], {"text": parts[1]} if len(parts) == 2 else {}, 100)

        query_tokens = self._expanded(self._tokens(text))
        best: ToolMatch = ToolMatch(None, {})
        for tool in self.tools.describe():
            name = tool["name"]
            candidate_tokens = self._expanded(self._tokens(f"{name} {tool['description']}"))
            score = len(query_tokens & candidate_tokens)
            if name.replace("_", " ") in lowered:
                score += 2
            if score > best.score:
                best = ToolMatch(name, {}, score)

        if best.score < self.threshold:
            return ToolMatch(None, {})
        return best

    def plan(self, query: str) -> ToolMatch:
        return self.match(query)
