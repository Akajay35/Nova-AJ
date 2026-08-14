from __future__ import annotations

from core.base_skill import BaseSkill


class StartupHistorySkill(BaseSkill):
    name = "startup_history"
    description = "Report the most recent startup diagnostic audit result."
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
        events = [e for e in audit.recent(20) if e.get("action") == "startup_diagnostics"]
        if not events:
            return "No startup diagnostic history is available yet."
        latest = events[-1]
        return f"The latest startup diagnostic was recorded as {latest['result']} at {latest['timestamp']}."
