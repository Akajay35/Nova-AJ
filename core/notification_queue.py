from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


class NotificationQueue:
    """Small persistent, provider-neutral queue for routed Nova alerts."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[dict]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, items: list[dict]) -> None:
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def enqueue(self, alert: dict) -> dict:
        item = {
            "id": uuid.uuid4().hex,
            "status": "queued",
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "channel": alert.get("channel", "digest"),
            "priority": alert.get("priority", "low"),
            "severity": alert.get("severity", "low"),
            "fingerprint": alert.get("fingerprint", ""),
            "title": alert.get("title", "Nova alert"),
            "action": alert.get("action", ""),
        }
        with self._lock:
            items = self._read()
            items.append(item)
            self._write(items[-500:])
        return item

    def list(self, status: str = "all") -> list[dict]:
        with self._lock:
            items = self._read()
        return [x for x in items if status == "all" or x.get("status") == status]
