from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class PersonalContext:
    """Small persistent profile/context store with explicit keys and bounded history."""
    def __init__(self, path: str = "data/personal_context.json", max_events: int = 100):
        self.path = Path(path); self.max_events = max_events
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({"profile": {}, "events": []})

    def _read(self) -> dict:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {"profile": {}, "events": []}

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def set(self, key: str, value: str) -> None:
        data = self._read(); data.setdefault("profile", {})[key.strip()] = value.strip(); self._write(data)

    def get(self, key: str, default=None): return self._read().get("profile", {}).get(key, default)

    def remember_event(self, text: str) -> None:
        data = self._read(); events = data.setdefault("events", [])
        events.append({"text": text.strip(), "created_at": datetime.now(timezone.utc).isoformat()})
        data["events"] = events[-self.max_events:]; self._write(data)

    def search(self, query: str) -> list[dict]:
        q = query.lower().strip()
        data = self._read(); return [e for e in data.get("events", []) if q in e.get("text", "").lower()]

    def snapshot(self) -> dict: return self._read()
