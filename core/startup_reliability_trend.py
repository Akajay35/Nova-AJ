from __future__ import annotations

from .startup_reliability import StartupReliability


class StartupReliabilityTrend:
    """Compare recent startup reliability with the preceding window."""

    def __init__(self, audit):
        self.audit = audit

    def assess(self, window: int = 5) -> dict[str, object]:
        events = [e for e in self.audit.recent(100) if e.get("action") == "startup_diagnostics"]
        if len(events) < 2:
            return {"trend": "stable", "current": None, "previous": None, "change": None}
        window = max(1, window)
        current_events = events[-window:]
        previous_events = events[-(window * 2):-window]
        current = round(sum(e.get("result") == "ready" for e in current_events) / len(current_events) * 100)
        previous = round(sum(e.get("result") == "ready" for e in previous_events) / len(previous_events) * 100) if previous_events else current
        change = current - previous
        trend = "improving" if change > 0 else "declining" if change < 0 else "stable"
        return {"trend": trend, "current": current, "previous": previous, "change": change}

    def summary(self, window: int = 5) -> str:
        result = self.assess(window)
        if result["current"] is None:
            return "Startup reliability trend is not available yet."
        change = result["change"]
        detail = f"{abs(change)} points" if change else "no change"
        return f"Startup reliability is {result['trend']} ({detail}). Current: {result['current']}/100; previous: {result['previous']}/100."
