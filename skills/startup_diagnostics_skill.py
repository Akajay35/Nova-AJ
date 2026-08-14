from __future__ import annotations

from core.base_skill import BaseSkill


class StartupDiagnosticsSkill(BaseSkill):
    name = "startup_diagnostics"
    description = "Run read-only startup diagnostics and explain Nova's current readiness."
    triggers = (
        "run startup diagnostics",
        "startup diagnostics",
        "check startup diagnostics",
        "check startup health",
    )

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(trigger in text for trigger in self.triggers)

    def handle(self, _query: str, context: dict) -> str:
        assistant = context.get("assistant")
        if assistant is None:
            return "The assistant context is unavailable."
        reporter = getattr(assistant, "startup_report", None)
        if reporter is None:
            return "Startup diagnostics are unavailable."
        return reporter.summary()
