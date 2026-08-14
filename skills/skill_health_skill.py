from __future__ import annotations

from core.base_skill import BaseSkill


class SkillHealthSkill(BaseSkill):
    name = "skill_health"
    description = "Read-only voice diagnostics for Nova's skill health."
    triggers = (
        "check your skill health",
        "check skill health",
        "skill health",
        "how healthy are your skills",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        monitor = getattr(assistant.skill_management, "health_monitor", None)
        if monitor is None:
            return "The skill health monitor is unavailable."
        result = monitor.check()
        return (
            f"Skill health is {result['state']} at {result['score']}/100. "
            f"I have {result['active']} active skills, {result['quarantined']} quarantined, "
            f"and {result['errors']} load errors."
        )
