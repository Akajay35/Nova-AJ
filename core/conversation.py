from __future__ import annotations

from collections import deque


class ConversationContext:
    """Small in-process conversation buffer; sensitive data is not persisted."""

    def __init__(self, limit: int = 12):
        self.messages = deque(maxlen=limit)

    def add(self, role: str, text: str) -> None:
        self.messages.append({"role": role, "text": text.strip()})

    def recent(self) -> list[dict]:
        return list(self.messages)

    def clear(self) -> None:
        self.messages.clear()
