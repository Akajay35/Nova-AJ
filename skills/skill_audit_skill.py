from __future__ import annotations

from core.base_skill import BaseSkill


class SkillAuditSkill(BaseSkill):
    name = "skill_audit"
    description = "Show recent skill-management audit activity."
    triggers = (
        "show recent skill management activity",
        "skill management activity",
        "skill audit log",
        "recent skill activity",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        audit = getattr(assistant.skill_management, "audit", None)
        if audit is None:
            return "Skill audit logging is unavailable."
        events = audit.recent(5)
        if not events:
            return "No skill-management activity has been recorded."
        parts = []
        for event in events:
            skill = f" for {event['skill']}" if event.get("skill") else ""
            parts.append(f"{event['action']} {event['result']}{skill}")
        return "Recent skill-management activity: " + "; ".join(parts) + "."
