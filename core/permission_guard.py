from __future__ import annotations
from dataclasses import dataclass
from typing import Callable


@dataclass
class PermissionDecision:
    allowed: bool
    reason: str
    needs_confirmation: bool = False


class PermissionGuard:
    """Gate skill actions without turning one-time confirmation into persistence."""

    def __init__(self, permission_manager, confirm: Callable[[str, str], bool] | None = None):
        self.permissions = permission_manager
        self.confirm = confirm

    def check(self, skill: str, permission: str, action: str = "") -> PermissionDecision:
        if permission not in self.permissions.configured(skill):
            return PermissionDecision(False, f"permission not configured: {permission}")

        if self.permissions.can_use(skill, permission):
            return PermissionDecision(True, "permission approved")

        if self.confirm and self.confirm(skill, permission):
            # Confirmation authorizes this execution only; do not persist it.
            return PermissionDecision(True, "one-time confirmation granted")

        return PermissionDecision(False, f"confirmation required: {permission}", True)

    def execute(self, skill: str, permission: str, action: str, fn):
        decision = self.check(skill, permission, action)
        if not decision.allowed:
            return decision
        return fn()
