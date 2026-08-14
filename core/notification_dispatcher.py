from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class Notification:
    title: str
    message: str
    source: str = "nova"

class NotificationDispatcher:
    """Routes reminder events to an injected notification sink; no platform I/O in core."""
    def __init__(self, sink: Callable[[Notification], None] | None = None):
        self.sink = sink or (lambda notification: None)

    def dispatch_reminder(self, reminder: dict) -> Notification:
        notification = Notification(
            title="Nova reminder",
            message=str(reminder.get("text", "You have a reminder.")),
            source="reminder",
        )
        self.sink(notification)
        return notification
