from __future__ import annotations

from core.base_skill import BaseSkill
from core.skill_permission_status import SkillPermissionStatus


class SkillPermissionStatusSkill(BaseSkill):
    name = "skill_permission_status"
    description = "Show current Nova skill-management permissions without changing them."
    triggers = (
        "what skill permissions are enabled",
        "skill permissions",
        "skill permission status",
        "what permissions are enabled",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        return SkillPermissionStatus(assistant.skill_permissions).summary()
