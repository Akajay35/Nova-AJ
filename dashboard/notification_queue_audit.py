from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


class NotificationQueueAudit:
    """Append-only local audit trail for protected queue-management actions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        *,
        actor: str,
        action: str,
        item_id: str,
        success: bool,
        reason: str = "",
    ) -> dict:
        event = {
            "id": uuid.uuid4().hex,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor or "unknown",
            "action": action,
            "item_id": item_id,
            "success": bool(success),
            "reason": reason,
        }
        with self._lock:
            try:
                existing = json.loads(self.path.read_text(encoding="utf-8"))
                events = existing if isinstance(existing, list) else []
            except (OSError, json.JSONDecodeError):
                events = []
            events.append(event)
            self.path.write_text(json.dumps(events[-1000:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return event

    def list(self) -> list[dict]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except (OSError, json.JSONDecodeError):
            return []
