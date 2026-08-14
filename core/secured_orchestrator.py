from __future__ import annotations

class SecuredOrchestrator:
    """Routes commands through permission/confirmation and records the outcome."""
    def __init__(self, router, handlers, guard, audit):
        self.router=router; self.handlers=handlers; self.guard=guard; self.audit=audit

    def handle(self, text: str):
        route=self.router.route(text); intent=route.intent
        handler=self.handlers.get(intent)
        if handler is None:
            self.audit.record("command", intent, text, "allowed", "chat")
            return route.response
        permission="memory_write" if intent=="memory" else "task_write" if intent=="task" else "skill_execute"
        decision=self.guard.check(intent, permission, text)
        if not decision.allowed:
            self.audit.record("command", intent, text, "denied", decision.reason)
            return {"status":"blocked", "reason":decision.reason}
        try:
            result=handler(text); self.audit.record("command", intent, text, "allowed", "success"); return result
        except Exception as exc:
            self.audit.record("command", intent, text, "allowed", f"error: {type(exc).__name__}")
            raise
