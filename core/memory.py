from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from config import MEMORY_FILE, MAX_MEMORY_ITEMS

class MemoryStore:
    def __init__(self, path: str = MEMORY_FILE):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self) -> list[dict]:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, data: list[dict]) -> None:
        self.path.write_text(json.dumps(data[-MAX_MEMORY_ITEMS:], indent=2, ensure_ascii=False), encoding="utf-8")
    def remember(self, text: str, kind: str = "fact") -> None:
        data = self._read(); data.append({"text": text.strip(), "kind": kind, "created_at": datetime.now(timezone.utc).isoformat()}); self._write(data)
    def recent(self, limit: int = 10) -> list[dict]: return self._read()[-limit:]
    def search(self, term: str) -> list[dict]:
        t = term.lower(); return [x for x in self._read() if t in x.get("text", "").lower()]
