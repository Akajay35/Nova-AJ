from __future__ import annotations

from core.base_skill import BaseSkill
from core.startup_reliability_trend import StartupReliabilityTrend


class StartupReliabilityTrendSkill(BaseSkill):
    name = "startup_reliability_trend"
    description = "Report whether Nova startup reliability is improving, declining, or stable."
    triggers = (
        "is your startup reliability improving",
        "is startup reliability improving",
        "startup reliability trend",
        "show startup reliability trend",
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
            return "Startup reliability trend is unavailable."
        return StartupReliabilityTrend(audit).summary()
