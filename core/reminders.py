from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class ReminderStore:
    def __init__(self, path: str = "data/reminders.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, data): self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def add(self, text: str, due_at: str | None = None) -> dict:
        items=self._read(); item={"id":len(items)+1,"text":text,"due_at":due_at,"completed":False,"created_at":datetime.now(timezone.utc).isoformat()}; items.append(item); self._write(items); return item
    def due(self, now: datetime | None = None):
        now=now or datetime.now(timezone.utc); result=[]
        for item in self._read():
            if item["completed"] or not item.get("due_at"): continue
            try:
                if datetime.fromisoformat(item["due_at"]) <= now: result.append(item)
            except ValueError: continue
        return result
    def complete(self, reminder_id: int) -> bool:
        items=self._read()
        for item in items:
            if item["id"] == reminder_id: item["completed"]=True; self._write(items); return True
        return False
