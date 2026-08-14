from __future__ import annotations

class SkillPermissionStatus:
    """Read-only view of enabled skill-management permissions."""
    def __init__(self, permissions):
        self.permissions = permissions

    def status(self) -> dict[str, object]:
        return {
            "read_actions": sorted(self.permissions.READ_ACTIONS),
            "recovery_enabled": bool(self.permissions.allow_recovery),
        }

    def summary(self) -> str:
        state = "enabled" if self.permissions.allow_recovery else "disabled"
        return f"Skill diagnostics, listing, and refresh are enabled. Skill recovery is {state}."
