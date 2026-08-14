from __future__ import annotations

from core.base_skill import BaseSkill


class SkillManagementSkill(BaseSkill):
    name = "skill_management"
    description = "Voice-accessible status and refresh controls for Nova skills."
    triggers = ("show skill status", "skill status", "refresh my skills", "refresh skills")

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, query: str, context: dict) -> str:
        management = context.get("skill_management")
        if management is None:
            return "The skill management service is unavailable."
        text = query.lower()
        if "refresh" in text:
            status = management.refresh()
            active = len(status["active"])
            quarantined = len(status["quarantined"])
            return f"Skill refresh complete. {active} active skills and {quarantined} quarantined skills."
        status = management.status()
        active = status["active"]
        quarantined = status["quarantined"]
        message = f"I have {len(active)} active skills."
        if quarantined:
            message += " Quarantined: " + ", ".join(quarantined) + "."
        return message
