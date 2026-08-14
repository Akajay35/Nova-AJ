from __future__ import annotations

from core.base_skill import BaseSkill
from core.skill_status import SkillStatus


class SkillStatusSkill(BaseSkill):
    name = "skill_status"
    description = "Show discovered Nova skills and refresh the skill registry."
    triggers = ("show my skills", "list skills", "skill status", "skill diagnostics", "refresh skills")

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        return SkillStatus(assistant.skills).summary()
