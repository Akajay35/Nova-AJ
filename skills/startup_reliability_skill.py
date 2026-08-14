from __future__ import annotations

from core.base_skill import BaseSkill
from core.startup_reliability import StartupReliability


class StartupReliabilitySkill(BaseSkill):
    name = "startup_reliability"
    description = "Report Nova's recent startup reliability score."
    triggers = (
        "how reliable have your startups been",
        "startup reliability",
        "how reliable are your startups",
        "show startup reliability",
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
            return "Startup reliability is unavailable."
        return StartupReliability(audit).summary()
