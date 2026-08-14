from __future__ import annotations

class SkillExecutionGateway:
    """Executes only an explicitly selected registered skill after authorization."""
    def __init__(self, registry, guard, audit):
        self.registry=registry; self.guard=guard; self.audit=audit

    def execute(self, skill_name: str, command: str, handler):
        skill=self.registry.get(skill_name)
        if not skill or not skill.get("enabled", False):
            return {"status":"blocked", "reason":"skill_unavailable"}
        permissions=skill.get("permissions", [])
        for permission in permissions:
            decision=self.guard.check("skill", permission, command)
            if not decision.allowed:
                self.audit.record("skill", skill_name, command, "denied", decision.reason)
                return {"status":"blocked", "reason":decision.reason}
        try:
            result=handler(command)
            self.audit.record("skill", skill_name, command, "allowed", "success")
            return {"status":"executed", "skill":skill_name, "result":result}
        except Exception as exc:
            self.audit.record("skill", skill_name, command, "error", type(exc).__name__)
            return {"status":"error", "skill":skill_name, "error":type(exc).__name__}
