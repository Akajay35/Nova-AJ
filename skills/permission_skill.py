from core.base_skill import BaseSkill
from core.skill_permissions import SkillPermissions

class PermissionSkill(BaseSkill):
    name = "permissions"
    description = "Configure and inspect skill permissions"
    keywords = ["grant permission", "revoke permission", "approve permission", "skill permissions"]

    def handle(self, query: str, context=None) -> str:
        permissions = context.get("skill_permissions") if context else SkillPermissions()
        q = query.lower().strip()
        if q.startswith("grant permission "):
            parts = q.removeprefix("grant permission ").split()
            if len(parts) != 2: return "Use: grant permission <skill> <permission>."
            return "Permission granted." if permissions.grant(*parts) else "Unknown permission."
        if q.startswith("revoke permission "):
            parts = q.removeprefix("revoke permission ").split()
            if len(parts) != 2: return "Use: revoke permission <skill> <permission>."
            permissions.revoke(*parts); return "Permission revoked."
        if q.startswith("approve permission "):
            parts = q.removeprefix("approve permission ").split()
            if len(parts) != 2: return "Use: approve permission <skill> <permission>."
            return "Approved for this session." if permissions.approve_once(*parts) else "Permission is not configured for that skill."
        return "Use grant, revoke, or approve permission commands."
