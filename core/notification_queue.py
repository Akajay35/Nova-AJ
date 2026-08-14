from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


class NotificationQueue:
    """Small persistent, provider-neutral queue for routed Nova alerts."""

    VALID_STATUSES = {"queued", "pending", "delivered", "failed"}

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
            "attempts": 0,
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

    def _update(self, item_id: str, status: str, error: str | None = None) -> dict | None:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"invalid notification status: {status}")
        with self._lock:
            items = self._read()
            for item in items:
                if item.get("id") == item_id:
                    item["status"] = status
                    item["updated_at"] = datetime.now(timezone.utc).isoformat()
                    if status in {"pending", "failed"}:
                        item["attempts"] = int(item.get("attempts", 0)) + (1 if status == "pending" else 0)
                    if status == "delivered":
                        item["delivered_at"] = item["updated_at"]
                    if error:
                        item["error"] = error
                    elif status != "failed":
                        item.pop("error", None)
                    self._write(items[-500:])
                    return dict(item)
        return None

    def mark_pending(self, item_id: str) -> dict | None:
        return self._update(item_id, "pending")

    def mark_delivered(self, item_id: str) -> dict | None:
        return self._update(item_id, "delivered")

    def mark_failed(self, item_id: str, error: str = "delivery failed") -> dict | None:
        return self._update(item_id, "failed", error)

    def retry_failed(self, item_id: str) -> dict | None:
        with self._lock:
            items = self._read()
            for item in items:
                if item.get("id") == item_id and item.get("status") == "failed":
                    item["status"] = "queued"
                    item["updated_at"] = datetime.now(timezone.utc).isoformat()
                    item["retry_at"] = item["updated_at"]
                    item.pop("error", None)
                    self._write(items[-500:])
                    return dict(item)
        return None

    def remove(self, item_id: str) -> bool:
        with self._lock:
            items = self._read()
            remaining = [x for x in items if x.get("id") != item_id]
            if len(remaining) == len(items):
                return False
            self._write(remaining)
            return True
