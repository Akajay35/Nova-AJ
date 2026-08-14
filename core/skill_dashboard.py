from __future__ import annotations

from .skill_permission_status import SkillPermissionStatus
from .skill_health import SkillHealth


class SkillDashboard:
    """Read-only unified snapshot of skill health, permissions, and recent activity."""
    def __init__(self, management):
        self.management = management

    def snapshot(self) -> dict[str, object]:
        status = self.management.status()
        permissions = SkillPermissionStatus(self.management.permissions).status()
        health = SkillHealth(self.management.manager, self.management.permissions).assess()
        audit = self.management.audit.recent(5)
        return {
            "active": status["active"],
            "quarantined": status["quarantined"],
            "errors": status["errors"],
            "health": health,
            "permissions": permissions,
            "recent_activity": audit,
        }

    def summary(self) -> str:
        data = self.snapshot()
        health = data["health"]
        message = f"Skill dashboard: {len(data['active'])} active, {len(data['quarantined'])} quarantined, {len(data['errors'])} current load errors. Health is {health['state']} at {health['score']}/100."
        recovery = "enabled" if data["permissions"]["recovery_enabled"] else "disabled"
        message += f" Recovery is {recovery}. {len(data['recent_activity'])} recent audit events recorded."
        return message
