from __future__ import annotations

from core.base_skill import BaseSkill
from core.skill_dashboard import SkillDashboard


class SkillDashboardSkill(BaseSkill):
    name = "skill_dashboard"
    description = "Show a unified, read-only overview of Nova skill health, permissions, and activity."
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
        return SkillDashboard(assistant.skill_management).summary()
