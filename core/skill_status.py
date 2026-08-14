from __future__ import annotations

class SkillStatus:
    """Read-only diagnostics for the currently discovered skill registry."""
    def __init__(self, manager):
        self.manager = manager
        self.last_error: str | None = None

    def refresh(self) -> dict:
        try:
            skills = self.manager.discover()
            self.last_error = None
            return {"ok": True, "count": len(skills), "skills": self.manager.names(), "error": None}
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {"ok": False, "count": 0, "skills": [], "error": self.last_error}

    def summary(self) -> str:
        status = self.refresh()
        if not status["ok"]:
            return f"Skill refresh failed: {status['error']}."
        if not status["skills"]:
            return "No skills are currently installed."
        return f"I found {status['count']} skills: " + ", ".join(status["skills"]) + "."
