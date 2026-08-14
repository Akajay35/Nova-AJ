from __future__ import annotations

from .skill_health import SkillHealth


class SkillHealthMonitor:
    """Detect health-state changes and record them in the skill audit log."""
    def __init__(self, manager, permissions, audit):
        self.health = SkillHealth(manager, permissions)
        self.audit = audit
        self._last_state: str | None = None
        self._last_score: int | None = None

    def check(self) -> dict[str, object]:
        current = self.health.assess()
        state = str(current["state"])
        score = int(current["score"])
        changed = self._last_state != state or self._last_score != score
        if changed and self._last_state is not None:
            self.audit.record("health_change", f"{self._last_state}->{state}")
        self._last_state = state
        self._last_score = score
        return {**current, "changed": changed}
