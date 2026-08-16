from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PendingAction:
    tool_name: str
    arguments: dict[str, Any]


class ConfirmationState:
    """In-memory confirmation gate for risky registered tools."""

    def __init__(self) -> None:
        self.pending: PendingAction | None = None

    def set(self, tool_name: str, arguments: dict[str, Any]) -> None:
        self.pending = PendingAction(tool_name, dict(arguments))

    def take(self) -> PendingAction | None:
        action = self.pending
        self.pending = None
        return action

    def clear(self) -> None:
        self.pending = None
