from __future__ import annotations

from core.base_skill import BaseSkill


class SkillRecoverySkill(BaseSkill):
    name = "skill_recovery"
    description = "Show quarantined skills and safely request recovery of a selected skill."
    triggers = ("show quarantined skills", "quarantined skills", "skill recovery", "recover skill")

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        manager = assistant.skills
        quarantined = manager.quarantined_skills()
        if "show quarantined" in query.lower() or "quarantined skills" in query.lower():
            return "No skills are quarantined." if not quarantined else "Quarantined skills: " + ", ".join(quarantined) + "."
        target = query.lower().split("recover skill", 1)[-1].strip(" :.-")
        if not target:
            return "Tell me which quarantined skill you want to recover."
        filename = target if target.endswith("_skill.py") else target + "_skill.py"
        if filename not in quarantined:
            return f"{filename} is not currently quarantined."
        manager.unquarantine(filename)
        return f"{filename} has been released from quarantine. It will be tested on the next skill refresh."
