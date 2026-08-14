from __future__ import annotations
from datetime import datetime, timezone

class SkillAuditLog:
    """Small in-memory audit trail for skill-management events."""
    def __init__(self, max_entries: int = 100):
        self.max_entries = max(1, max_entries)
        self.events: list[dict[str, str]] = []

    def record(self, action: str, result: str, skill: str | None = None) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "result": result,
        }
        if skill:
            event["skill"] = skill
        self.events.append(event)
        if len(self.events) > self.max_entries:
            self.events = self.events[-self.max_entries:]

    def recent(self, limit: int = 10) -> list[dict[str, str]]:
        return list(self.events[-max(1, limit):])

    def summary(self) -> str:
        if not self.events:
            return "No skill-management events have been recorded."
        return f"{len(self.events)} skill-management events are recorded."
