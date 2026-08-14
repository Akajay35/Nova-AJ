from __future__ import annotations

from core.base_skill import BaseSkill


class SkillManagementSkill(BaseSkill):
    name = "skill_management"
    description = "Natural-language status and refresh controls for Nova skills."
    triggers = (
        "show skill status", "skill status", "refresh my skills", "refresh skills",
        "what skills do you have", "which skills do you have", "list your skills",
        "which skills are disabled", "are any skills disabled", "are any skills broken",
        "which skills are broken", "skill diagnostics",
    )

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
            return self._summary(status, "Skill refresh complete.")
        status = management.status()
        if any(word in text for word in ("broken", "failed", "diagnostic")):
            errors = status.get("errors", [])
            return "No skill load failures are recorded." if not errors else "Skill load failures: " + "; ".join(item["skill"] + " (" + item["error"] + ")" for item in errors) + "."
        if "disabled" in text or "quarantined" in text:
            quarantined = status.get("quarantined", [])
            return "No skills are disabled or quarantined." if not quarantined else "Quarantined skills: " + ", ".join(quarantined) + "."
        return self._summary(status)

    @staticmethod
    def _summary(status: dict, prefix: str = "") -> str:
        message = (prefix + " " if prefix else "") + f"I have {len(status['active'])} active skills."
        if status.get("quarantined"):
            message += " Quarantined: " + ", ".join(status["quarantined"]) + "."
        return message
