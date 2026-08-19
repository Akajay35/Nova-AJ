from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config import MEMORY_FILE, MAX_MEMORY_ITEMS


class MemoryStore:
    """Persistent local memory with explicit, bounded remember/search/forget controls."""

    MAX_TEXT_LENGTH = 4096
    MAX_KIND_LENGTH = 64

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
            return [item for item in data if self._valid_item(item)]
        except (OSError, json.JSONDecodeError):
            return []

    @classmethod
    def _valid_item(cls, item: object) -> bool:
        if not isinstance(item, dict):
            return False
        text = item.get("text", "")
        kind = item.get("kind", "")
        return (
            isinstance(text, str) and 0 < len(text) <= cls.MAX_TEXT_LENGTH
            and isinstance(kind, str) and 0 < len(kind) <= cls.MAX_KIND_LENGTH
        )

    def _write(self, data: list[dict]) -> None:
        self.path.write_text(
            json.dumps(data[-MAX_MEMORY_ITEMS:], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def remember(self, text: str, kind: str = "fact") -> dict:
        value = str(text).strip()
        category = str(kind).strip() or "fact"
        if not value:
            raise ValueError("Memory text cannot be empty")
        if len(value) > self.MAX_TEXT_LENGTH:
            raise ValueError("Memory text is too long")
        if len(category) > self.MAX_KIND_LENGTH:
            raise ValueError("Memory kind is too long")
        item = {
            "id": uuid4().hex,
            "text": value,
            "kind": category,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data = self._read()
        data.append(item)
        self._write(data)
        return item

    def recent(self, limit: int = 10) -> list[dict]:
        try:
            limit = max(0, min(int(limit), MAX_MEMORY_ITEMS))
        except (TypeError, ValueError):
            limit = 10
        return self._read()[-limit:]

    def search(self, term: str, kind: str | None = None) -> list[dict]:
        value = str(term).strip().lower()
        if not value:
            return []
        requested_kind = kind.strip().lower() if isinstance(kind, str) and kind.strip() else None
        return [
            item for item in self._read()
            if value in item["text"].lower()
            and (requested_kind is None or item["kind"].lower() == requested_kind)
        ]

    def forget(self, memory_id: str) -> bool:
        target = str(memory_id).strip()
        if not target:
            return False
        data = self._read()
        remaining = [item for item in data if item.get("id") != target]
        if len(remaining) == len(data):
            return False
        self._write(remaining)
        return True

    def forget_matching(self, term: str) -> int:
        value = str(term).strip().lower()
        if not value:
            return 0
        data = self._read()
        remaining = [item for item in data if value not in item["text"].lower()]
        removed = len(data) - len(remaining)
        if removed:
            self._write(remaining)
        return removed

    def all(self) -> list[dict]:
        return self._read()

    def health(self) -> dict[str, object]:
        try:
            count = len(self._read())
            writable = self.path.parent.exists() and self.path.parent.is_dir()
            return {"available": writable, "status": "ready" if writable else "unavailable", "count": count}
        except OSError:
            return {"available": False, "status": "unavailable", "count": 0}
