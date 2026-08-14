from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class StartupAlertStore:
    """Persist startup alert history in a small local JSON file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> list[dict]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save(self, history: list[dict]) -> list[dict]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return history

    def sync(self, alerts: list[dict], timestamp: str | None = None) -> list[dict]:
        now = timestamp or datetime.now(timezone.utc).isoformat()
        history = self.load()
        active = {str(a.get("severity", "info")): a for a in alerts}
        active_entries = {str(e.get("severity")): e for e in history if e.get("status") == "active"}

        for severity, alert in active.items():
            entry = active_entries.get(severity)
            if entry is None:
                history.append({"severity": severity, "title": alert.get("title", "Startup alert"), "count": alert.get("count", 0), "action": alert.get("action", ""), "appeared_at": now, "resolved_at": None, "status": "active"})
            else:
                entry["count"] = alert.get("count", entry.get("count", 0))
                entry["action"] = alert.get("action", entry.get("action", ""))

        for entry in history:
            severity = str(entry.get("severity", "info"))
            if entry.get("status") == "active" and severity not in active:
                entry["status"] = "resolved"
                entry["resolved_at"] = now

        return self.save(history)
