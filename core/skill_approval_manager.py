from __future__ import annotations

class SkillApprovalManager:
    """Tracks explicit approval for staged skills before they can be enabled."""
    def __init__(self, registry):
        self.registry = registry
        self._decisions: dict[str, dict] = {}

    def approve(self, name: str, reviewer: str = "user"):
        skill = self.registry.get(name)
        if not skill:
            return {"status": "not_found", "skill": name}
        self._decisions[name] = {"approved": True, "reviewer": reviewer}
        return {"status": "approved", "skill": name, "reviewer": reviewer}

    def reject(self, name: str, reason: str = "rejected", reviewer: str = "user"):
        if not self.registry.get(name):
            return {"status": "not_found", "skill": name}
        self._decisions[name] = {"approved": False, "reviewer": reviewer, "reason": reason}
        self.registry.disable(name)
        return {"status": "rejected", "skill": name, "reason": reason}

    def enable_if_approved(self, name: str):
        decision = self._decisions.get(name)
        if not decision or not decision.get("approved"):
            return {"status": "blocked", "reason": "approval_required", "skill": name}
        enabled = self.registry.enable(name)
        return {"status": "enabled" if enabled else "not_found", "skill": name}

    def decision(self, name: str):
        return self._decisions.get(name)
