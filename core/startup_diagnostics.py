from __future__ import annotations

class StartupDiagnostics:
    """Format a safe, actionable startup-readiness report and audit the result."""
    def __init__(self, assistant):
        self.assistant = assistant

    def run(self) -> dict[str, object]:
        health = self.assistant.health.run()
        skills = self.assistant.skill_management.refresh()
        issues: list[str] = []
        if not health.get("ok"):
            issues.append("one or more core components need attention")
        if skills.get("errors"):
            issues.append(f"{len(skills['errors'])} skill load error(s)")
        if skills.get("quarantined"):
            issues.append(f"{len(skills['quarantined'])} skill(s) quarantined")
        ready = not issues
        audit = getattr(self.assistant.skill_management, "audit", None)
        if audit is not None:
            audit.record("startup_diagnostics", "ready" if ready else "needs_attention")
        return {"ready": ready, "issues": issues, "health": health, "skills": skills}

    def summary(self) -> str:
        result = self.run()
        if result["ready"]:
            return "Startup diagnostics: all checked systems are ready and no skill issues were detected."
        return "Startup diagnostics: " + "; ".join(result["issues"]) + "."
