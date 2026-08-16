from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HISTORY_FILE = Path("data/conversation_history.json")


class ConversationHistory:
    """Persistent, bounded conversation history kept separate from profile memory."""

    def __init__(self, path: str | Path = HISTORY_FILE, limit: int = 100) -> None:
        self.path = Path(path)
        self.limit = max(1, int(limit))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]

    def _write(self, entries: list[dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(entries[-self.limit :], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, role: str, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Conversation text cannot be empty")
        entry = {
            "role": role.strip(),
            "text": cleaned,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        entries = self._read()
        entries.append(entry)
        self._write(entries)
        return entry

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if limit < 1:
            return []
        return self._read()[-min(limit, self.limit) :]

    def clear(self) -> None:
        self._write([])

    def count(self) -> int:
        return len(self._read())
