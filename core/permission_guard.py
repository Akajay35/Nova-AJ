from __future__ import annotations
from dataclasses import dataclass
from typing import Callable


@dataclass
class PermissionDecision:
    allowed: bool
    reason: str
    needs_confirmation: bool = False


class PermissionGuard:
    """Gate skill actions through explicit permissions and one-time confirmation."""

    def __init__(
        self,
        permission_manager,
        confirm: Callable[[str, str], bool] | None = None,
    ):
        self.permissions = permission_manager
        self.confirm = confirm

    def check(self, skill: str, permission: str, action: str = "") -> PermissionDecision:
        if self.permissions.allowed(skill, permission):
            return PermissionDecision(True, "permission granted")

        if self.confirm and self.confirm(skill, permission):
            # A normal confirmation authorizes this execution only. Persistent
            # permission must be granted through the permission manager's
            # explicit user-facing "always allow" flow.
            return PermissionDecision(True, "one-time confirmation granted")

        return PermissionDecision(False, f"permission required: {permission}", True)

    def execute(self, skill: str, permission: str, action: str, fn):
        decision = self.check(skill, permission, action)
        if not decision.allowed:
            return decision
        return fn()
