from __future__ import annotations

class SkillHealth:
    """Compute a simple deterministic health state from skill diagnostics."""
    def __init__(self, manager, permissions):
        self.manager = manager
        self.permissions = permissions

    def assess(self) -> dict[str, object]:
        active = len(self.manager.names())
        quarantined = len(self.manager.quarantined_skills())
        errors = len(self.manager.errors())
        if errors or quarantined:
            state = "degraded"
        elif active:
            state = "healthy"
        else:
            state = "empty"
        score = 100
        if quarantined:
            score -= min(50, quarantined * 15)
        if errors:
            score -= min(50, errors * 10)
        score = max(0, score)
        return {
            "state": state,
            "score": score,
            "active": active,
            "quarantined": quarantined,
            "errors": errors,
            "recovery_enabled": bool(self.permissions.allow_recovery),
        }

    def summary(self) -> str:
        result = self.assess()
        return f"Skill health is {result['state']} with a score of {result['score']}/100: {result['active']} active, {result['quarantined']} quarantined, {result['errors']} load errors."
