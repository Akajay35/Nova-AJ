from __future__ import annotations

from .skill_permissions import SkillPermissions
from .skill_audit import SkillAuditLog
from .skill_health_monitor import SkillHealthMonitor


class SkillManagement:
    """Permission-aware facade for safe skill discovery, recovery, and health monitoring."""
    def __init__(self, manager, permissions: SkillPermissions | None = None, audit: SkillAuditLog | None = None):
        self.manager = manager
        self.permissions = permissions or SkillPermissions()
        self.audit = audit or SkillAuditLog()
        self.health_monitor = SkillHealthMonitor(self.manager, self.permissions, self.audit)

    def status(self) -> dict:
        return {"active": self.manager.names(), "quarantined": self.manager.quarantined_skills(), "errors": self.manager.errors()}

    def refresh(self) -> dict:
        if not self.permissions.allowed("refresh"):
            self.audit.record("refresh", "denied")
            return {"ok": False, "message": self.permissions.explain("refresh")}
        self.audit.record("discover", "success")
        self.manager.load()
        status = self.status()
        health = self.health_monitor.check()
        self.audit.record("refresh", "success" if not status["errors"] else "completed_with_errors")
        status["health"] = health
        return status

    def recover(self, filename: str) -> dict:
        if not self.permissions.allowed("recover"):
            self.audit.record("recover", "denied", filename)
            return {"ok": False, "message": self.permissions.explain("recover")}
        if filename not in self.manager.quarantined_skills():
            self.audit.record("recover", "not_quarantined", filename)
            return {"ok": False, "message": f"{filename} is not quarantined."}
        self.manager.unquarantine(filename)
        self.audit.record("recover", "released", filename)
        return {"ok": True, "message": f"{filename} released for the next refresh."}
