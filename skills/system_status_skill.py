from __future__ import annotations

from core.base_skill import BaseSkill
from core.system_status import SystemStatus


class SystemStatusSkill(BaseSkill):
    name = "system_status"
    description = "Read-only overall status diagnostics for Nova."
    triggers = (
        "check your system status",
        "check system status",
        "system status",
        "how is your system",
        "are you ready",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        return SystemStatus(assistant).summary()
