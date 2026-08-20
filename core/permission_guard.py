from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class PermissionDecision:
    allowed: bool
    reason: str
    needs_confirmation: bool=False

class PermissionGuard:
    """Gate skill actions; explicit confirmation may authorize one execution only."""
    def __init__(self,permission_manager,confirm:Callable[[str,str],bool]|None=None): self.permissions=permission_manager; self.confirm=confirm
    def check(self,skill,permission,action=""):
        configured=permission in self.permissions.configured(skill)
        if configured and self.permissions.can_use(skill,permission): return PermissionDecision(True,"permission approved")
        if self.confirm and self.confirm(skill,permission): return PermissionDecision(True,"one-time confirmation granted")
        if not configured: return PermissionDecision(False,f"permission not configured: {permission}")
        return PermissionDecision(False,f"confirmation required: {permission}",True)
    def execute(self,skill,permission,action,fn):
        decision=self.check(skill,permission,action)
        return fn() if decision.allowed else decision
