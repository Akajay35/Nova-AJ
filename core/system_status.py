from __future__ import annotations

from .skill_dashboard import SkillDashboard


class SystemStatus:
    """Read-only consolidated status for the Nova personal assistant."""
    def __init__(self, assistant):
        self.assistant = assistant

    def snapshot(self) -> dict[str, object]:
        health = self.assistant.health.run()
        skills = SkillDashboard(self.assistant.skill_management).snapshot()
        startup = None
        reporter = getattr(self.assistant, "startup_report", None)
        if reporter is not None:
            startup = reporter.run()
        return {
            "ready": bool(health.get("ok")) and (startup is None or bool(startup.get("ready"))),
            "health": health,
            "skills": skills,
            "startup": startup,
        }

    def summary(self) -> str:
        data = self.snapshot()
        skill_health = data["skills"]["health"]
        readiness = "ready" if data["ready"] else "needs attention"
        message = (
            f"Nova system status: {readiness}. Skill health is {skill_health['state']} "
            f"at {skill_health['score']}/100, with {skill_health['active']} active skills, "
            f"{skill_health['quarantined']} quarantined, and {skill_health['errors']} load errors."
        )
        startup = data.get("startup")
        if startup and startup.get("issues"):
            message += " Startup issues: " + "; ".join(startup["issues"]) + "."
        return message
