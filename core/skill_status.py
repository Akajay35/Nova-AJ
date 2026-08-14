from __future__ import annotations

class SkillStatus:
    """Read-only diagnostics for the discovered skill registry and load failures."""
    def __init__(self, manager):
        self.manager = manager
        self.last_error: str | None = None

    def refresh(self) -> dict:
        try:
            skills = self.manager.discover()
            self.last_error = None
            errors = self.manager.errors() if hasattr(self.manager, "errors") else []
            return {
                "ok": not errors,
                "count": len(skills),
                "skills": self.manager.names(),
                "failed_count": len(errors),
                "errors": errors,
                "error": None if not errors else "skill_load_errors",
            }
        except Exception as exc:
            self.last_error = type(exc).__name__
            return {"ok": False, "count": 0, "skills": [], "failed_count": 0, "errors": [], "error": self.last_error}

    def summary(self) -> str:
        status = self.refresh()
        if not status["ok"] and status["error"] != "skill_load_errors":
            return f"Skill diagnostics failed: {status['error']}."
        message = f"I found {status['count']} working skills."
        if status["failed_count"]:
            failed = ", ".join(item["skill"] for item in status["errors"])
            message += f" {status['failed_count']} failed to load: {failed}."
        elif not status["skills"]:
            message = "No skills are currently installed."
        return message
