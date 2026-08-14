from __future__ import annotations

class HealthSkill:
    """Provides a read-only voice-friendly system health capability."""
    name = "system_health"

    def __init__(self, health_check):
        self.health_check = health_check

    def handle(self, _command: str = "") -> str:
        result = self.health_check.run()
        failed = [name for name, item in result["checks"].items() if not item["ok"]]
        if not failed:
            return "All Nova core components are healthy."
        return "These Nova components need attention: " + ", ".join(failed) + "."
