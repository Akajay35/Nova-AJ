from __future__ import annotations

class StartupHistory:
    """Read-only summary of recent startup diagnostic audit events."""
    def __init__(self, audit):
        self.audit = audit

    def recent(self, limit: int = 5) -> list[dict[str, str]]:
        events = [event for event in self.audit.recent(100) if event.get("action") == "startup_diagnostics"]
        return events[-max(1, limit):]

    def summary(self, limit: int = 5) -> str:
        events = self.recent(limit)
        if not events:
            return "No startup diagnostic history is available yet."
        results = ", ".join(event["result"] for event in events)
        return f"Recent startup diagnostics ({len(events)}): {results}."
