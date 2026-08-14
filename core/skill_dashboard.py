from __future__ import annotations

from .skill_permission_status import SkillPermissionStatus


class SkillDashboard:
    """Read-only unified snapshot of skill health, permissions, and recent activity."""
    def __init__(self, management):
        self.management = management

    def snapshot(self) -> dict[str, object]:
        status = self.management.status()
        permissions = SkillPermissionStatus(self.management.permissions).status()
        audit = self.management.audit.recent(5)
        return {
            "active": status["active"],
            "quarantined": status["quarantined"],
            "errors": status["errors"],
            "permissions": permissions,
            "recent_activity": audit,
        }

    def summary(self) -> str:
        data = self.snapshot()
        message = f"Skill dashboard: {len(data['active'])} active, {len(data['quarantined'])} quarantined, {len(data['errors'])} current load errors."
        recovery = "enabled" if data["permissions"]["recovery_enabled"] else "disabled"
        message += f" Recovery is {recovery}. {len(data['recent_activity'])} recent audit events recorded."
        return message
