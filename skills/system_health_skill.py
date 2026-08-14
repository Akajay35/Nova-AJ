from __future__ import annotations
from core.base_skill import BaseSkill

class SystemHealthSkill(BaseSkill):
    name = "system_health"
    description = "Reports the health of Nova core components."
    keywords = ["system health", "health check", "check your system", "check system", "are you healthy", "diagnostics"]
    risk_level = "low"

    def handle(self, query: str, context=None) -> str:
        health = (context or {}).get("health")
        if health is None:
            return "System health diagnostics are not connected yet."
        result = health.run()
        failed = [name for name, item in result["checks"].items() if not item["ok"]]
        return "All Nova core components are healthy." if not failed else "These Nova components need attention: " + ", ".join(failed) + "."
