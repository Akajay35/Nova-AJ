from __future__ import annotations

from .skill_permissions import SkillPermissions


class SkillManagement:
    """Permission-aware facade for safe skill discovery and controlled recovery."""
    def __init__(self, manager, permissions: SkillPermissions | None = None):
        self.manager = manager
        self.permissions = permissions or SkillPermissions()

    def status(self) -> dict:
        return {"active": self.manager.names(), "quarantined": self.manager.quarantined_skills(), "errors": self.manager.errors()}

    def refresh(self) -> dict:
        if not self.permissions.allowed("refresh"):
            return {"ok": False, "message": self.permissions.explain("refresh")}
        self.manager.discover()
        return self.status()

    def recover(self, filename: str) -> dict:
        if not self.permissions.allowed("recover"):
            return {"ok": False, "message": self.permissions.explain("recover")}
        if filename not in self.manager.quarantined_skills():
            return {"ok": False, "message": f"{filename} is not quarantined."}
        self.manager.unquarantine(filename)
        return {"ok": True, "message": f"{filename} released for the next refresh."}
