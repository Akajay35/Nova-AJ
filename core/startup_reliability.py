from __future__ import annotations


class StartupReliability:
    """Compute a bounded reliability score from recent startup diagnostic results."""

    def __init__(self, audit):
        self.audit = audit

    def recent(self, limit: int = 5) -> list[dict[str, str]]:
        events = [
            event for event in self.audit.recent(100)
            if event.get("action") == "startup_diagnostics"
        ]
        return events[-max(1, limit):]

    def assess(self, limit: int = 5) -> dict[str, object]:
        events = self.recent(limit)
        if not events:
            return {"score": None, "ready": None, "checks": 0}
        ready = sum(1 for event in events if event.get("result") == "ready")
        score = round((ready / len(events)) * 100)
        return {"score": score, "ready": score == 100, "checks": len(events)}

    def summary(self, limit: int = 5) -> str:
        result = self.assess(limit)
        if result["score"] is None:
            return "Startup reliability is not available yet."
        return f"Startup reliability is {result['score']}/100 across {result['checks']} recent checks."
