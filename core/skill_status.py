from __future__ import annotations

class SkillStatus:
    """Read-only diagnostics for skills, load failures, and quarantine state."""
    def __init__(self, manager):
        self.manager = manager
        self.last_error: str | None = None

    def refresh(self) -> dict:
        try:
            skills = self.manager.discover()
            self.last_error = None
            errors = self.manager.errors() if hasattr(self.manager, "errors") else []
            quarantined = self.manager.quarantined_skills() if hasattr(self.manager, "quarantined_skills") else []
            return {
                "ok": not errors,
                "count": len(skills),
                "skills": self.manager.names(),
                "failed_count": len(errors),
                "errors": errors,
                "quarantined_count": len(quarantined),
                "quarantined": quarantined,
                "error": None if not errors else "skill_load_errors",
            }
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {"ok": False, "count": 0, "skills": [], "failed_count": 0, "errors": [], "quarantined_count": 0, "quarantined": [], "error": self.last_error}

    def summary(self) -> str:
        status = self.refresh()
        if not status["ok"] and status["error"] != "skill_load_errors":
            return f"Skill diagnostics failed: {status['error']}."
        message = f"I found {status['count']} working skills."
        if status["failed_count"]:
            failed = ", ".join(item["skill"] for item in status["errors"])
            message += f" {status['failed_count']} failed to load: {failed}."
        if status["quarantined_count"]:
            message += " Quarantined: " + ", ".join(status["quarantined"]) + "."
        if not status["skills"] and not status["quarantined"]:
            message = "No skills are currently installed."
        return message
