from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

class ProjectManager:
    def __init__(self, path: str = "data/projects.json"):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, data): self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def create(self, name: str, goal: str = "") -> dict:
        items=self._read(); item={"id":len(items)+1,"name":name,"goal":goal,"status":"active","created_at":datetime.now(timezone.utc).isoformat()}; items.append(item); self._write(items); return item
    def list(self): return self._read()
    def update_status(self, project_id: int, status: str) -> bool:
        items=self._read()
        for item in items:
            if item["id"] == project_id: item["status"]=status; self._write(items); return True
        return False
