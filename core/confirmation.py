from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class ConfirmationRequest:
    action: str
    skill: str
    permission: str

@dataclass
class ConfirmationResult:
    approved: bool
    reason: str

class ConfirmationManager:
    """Central approval gate for sensitive assistant actions."""
    def __init__(self, prompt: Callable[[ConfirmationRequest], bool] | None = None):
        self.prompt = prompt

    def request(self, action: str, skill: str, permission: str) -> ConfirmationResult:
        request = ConfirmationRequest(action, skill, permission)
        if self.prompt is None:
            return ConfirmationResult(False, "confirmation required")
        approved = bool(self.prompt(request))
        return ConfirmationResult(approved, "approved" if approved else "denied")
