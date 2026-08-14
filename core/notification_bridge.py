from __future__ import annotations
from collections.abc import Callable

class NotificationBridge:
    """Route scheduler events to a UI or voice callback without owning OS notification APIs."""
    def __init__(self, callback: Callable[[str], None] | None = None):
        self.callback = callback
        self.history: list[str] = []

    def notify(self, message: str) -> str:
        text = str(message).strip()
        if not text:
            return ""
        self.history.append(text)
        if self.callback:
            self.callback(text)
        return text

    def last(self) -> str | None:
        return self.history[-1] if self.history else None

    def clear(self) -> None:
        self.history.clear()
