from __future__ import annotations

from core.base_skill import BaseSkill


class SkillDashboardSkill(BaseSkill):
    name = "skill_dashboard"
    description = "Show a unified, read-only overview of Nova skill health and permissions."
    triggers = (
        "show my skill dashboard",
        "skill dashboard",
        "show skill dashboard",
        "skill health dashboard",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        manager = assistant.skills
        status = manager.names()
        quarantined = manager.quarantined_skills()
        errors = manager.errors()
        permissions = assistant.skill_permissions
        audit = getattr(assistant.skill_management, "audit", None)
        events = audit.recent(5) if audit else []
        recovery = "enabled" if permissions.allow_recovery else "disabled"
        message = f"Skill dashboard: {len(status)} active, {len(quarantined)} quarantined, {len(errors)} current load errors. Recovery is {recovery}."
        if events:
            message += f" {len(events)} recent audit events available."
        return message
