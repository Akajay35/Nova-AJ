from __future__ import annotations

from core.base_skill import BaseSkill
from core.startup_history import StartupHistory


class StartupHistorySkill(BaseSkill):
    name = "startup_history"
    description = "Report recent startup diagnostic audit history."
    triggers = (
        "what happened during your last startup check",
        "last startup check",
        "startup history",
        "show startup history",
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
            return "Startup audit history is unavailable."
        return StartupHistory(audit).summary()
