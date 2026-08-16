from __future__ import annotations

from collections import deque
import re


class ConversationContext:
    """Small in-process conversation buffer with bounded follow-up context."""

    _REFERENCE_RE = re.compile(r"\b(he|she|they|them|his|her|their|it|that person)\b", re.IGNORECASE)
    _SUBJECT_PATTERNS = (
        re.compile(r"(?:search|look up|find)\s+(?:for\s+)?(.+?)(?:\s+on\s+(?:the\s+)?(?:web|wikipedia))?\s*$", re.I),
        re.compile(r"(?:tell me about|who is|what is)\s+(.+?)\s*$", re.I),
    )

    def __init__(self, limit: int = 12):
        self.messages = deque(maxlen=limit)
        self.last_subject: str | None = None

    def add(self, role: str, text: str) -> None:
        cleaned = text.strip()
        self.messages.append({"role": role, "text": cleaned})
        if role == "user":
            self._learn_subject(cleaned)

    def _learn_subject(self, text: str) -> None:
        for pattern in self._SUBJECT_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            candidate = match.group(1).strip(" .?!")
            if candidate and len(candidate) <= 120:
                self.last_subject = candidate
                return

    def observe_tool_result(self, tool_name: str | None, text: str) -> None:
        """Capture a useful entity from bounded information-tool results."""
        if tool_name != "web_search":
            return
        first_line = text.strip().splitlines()[0] if text.strip() else ""
        candidate = first_line.split(":", 1)[0].strip()
        if candidate and candidate.lower() not in {"no web results found"} and len(candidate) <= 120:
            self.last_subject = candidate

    def resolve(self, text: str) -> str:
        """Resolve simple follow-up references without inventing context."""
        cleaned = text.strip()
        if not cleaned or not self.last_subject or not self._REFERENCE_RE.search(cleaned):
            return cleaned
        return self._REFERENCE_RE.sub(self.last_subject, cleaned)

    def recent(self) -> list[dict]:
        return list(self.messages)

    def clear(self) -> None:
        self.messages.clear()
        self.last_subject = None
