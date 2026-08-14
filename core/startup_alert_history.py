from __future__ import annotations

from datetime import datetime, timezone


class StartupAlertHistory:
    """Keep a small local history of startup alerts and their resolution."""

    def __init__(self):
        self._history: list[dict] = []
        self._active: dict[str, dict] = {}

    def record(self, alerts: list[dict], timestamp: str | None = None) -> list[dict]:
        now = timestamp or datetime.now(timezone.utc).isoformat()
        current = {str(a.get("severity", "info")): a for a in alerts}

        for severity, alert in current.items():
            if severity not in self._active:
                entry = {"severity": severity, "title": alert.get("title", "Startup alert"), "count": alert.get("count", 0), "action": alert.get("action", ""), "appeared_at": now, "resolved_at": None, "status": "active"}
                self._history.append(entry)
                self._active[severity] = entry
            else:
                entry = self._active[severity]
                entry["count"] = alert.get("count", entry["count"])

        for severity in list(self._active):
            if severity not in current:
                entry = self._active.pop(severity)
                entry["resolved_at"] = now
                entry["status"] = "resolved"

        return list(self._history)

    def active(self) -> list[dict]:
        return [x for x in self._history if x["status"] == "active"]

    def all(self) -> list[dict]:
        return list(self._history)
