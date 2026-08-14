from __future__ import annotations
from typing import Callable

class AuditedActionExecutor:
    """Combines permission, confirmation, execution and audit logging."""
    def __init__(self, guard, audit_log):
        self.guard=guard; self.audit=audit_log

    def run(self, skill: str, permission: str, action: str, fn: Callable[[], object]):
        decision=self.guard.check(skill, permission, action)
        if not decision.allowed:
            self.audit.record("action", skill, action, "denied", decision.reason)
            return decision
        try:
            result=fn()
            self.audit.record("action", skill, action, "allowed", "success")
            return result
        except Exception as exc:
            self.audit.record("action", skill, action, "allowed", f"error: {type(exc).__name__}")
            raise
