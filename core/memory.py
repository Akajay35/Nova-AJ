from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config import MEMORY_FILE, MAX_MEMORY_ITEMS


class MemoryStore:
    """Persistent local memory with explicit remember, search, and forget controls."""

    def __init__(self, path: str = MEMORY_FILE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [item for item in data if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, data: list[dict]) -> None:
        self.path.write_text(
            json.dumps(data[-MAX_MEMORY_ITEMS:], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def remember(self, text: str, kind: str = "fact") -> dict:
        value = text.strip()
        if not value:
            raise ValueError("Memory text cannot be empty")
        item = {
            "id": uuid4().hex,
            "text": value,
            "kind": kind.strip() or "fact",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data = self._read()
        data.append(item)
        self._write(data)
        return item

    def recent(self, limit: int = 10) -> list[dict]:
        return self._read()[-max(0, limit):]

    def search(self, term: str, kind: str | None = None) -> list[dict]:
        value = term.strip().lower()
        requested_kind = kind.strip().lower() if kind else None
        return [
            item
            for item in self._read()
            if value in item.get("text", "").lower()
            and (requested_kind is None or item.get("kind", "").lower() == requested_kind)
        ]

    def forget(self, memory_id: str) -> bool:
        target = memory_id.strip()
        data = self._read()
        remaining = [item for item in data if item.get("id") != target]
        if len(remaining) == len(data):
            return False
        self._write(remaining)
        return True

    def forget_matching(self, term: str) -> int:
        value = term.strip().lower()
        if not value:
            return 0
        data = self._read()
        remaining = [item for item in data if value not in item.get("text", "").lower()]
        removed = len(data) - len(remaining)
        if removed:
            self._write(remaining)
        return removed

    def all(self) -> list[dict]:
        return self._read()
