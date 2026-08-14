from __future__ import annotations

from .skill_dashboard import SkillDashboard


class SystemStatus:
    """Read-only consolidated status for the Nova personal assistant."""
    def __init__(self, assistant):
        self.assistant = assistant

    def snapshot(self) -> dict[str, object]:
        health = self.assistant.health.run()
        skills = SkillDashboard(self.assistant.skill_management).snapshot()
        return {
            "ready": bool(health.get("ok")),
            "health": health,
            "skills": skills,
        }

    def summary(self) -> str:
        data = self.snapshot()
        skill_health = data["skills"]["health"]
        readiness = "ready" if data["ready"] else "needs attention"
        return (
            f"Nova system status: {readiness}. Skill health is {skill_health['state']} "
            f"at {skill_health['score']}/100, with {skill_health['active']} active skills, "
            f"{skill_health['quarantined']} quarantined, and {skill_health['errors']} load errors."
        )
