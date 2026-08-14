from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass
class Task:
    id: str
    title: str
    due_at: str | None = None
    recurring: str | None = None
    completed: bool = False
    created_at: str = ""

class TaskStore:
    """Local task/reminder store with explicit completion and deletion."""
    def __init__(self, path: str = "data/tasks.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, items): self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    def add(self, task: Task) -> Task:
        if not task.created_at: task.created_at=datetime.now(timezone.utc).isoformat()
        items=self._read(); items.append(asdict(task)); self._write(items); return task
    def pending(self): return [x for x in self._read() if not x.get("completed")]
    def complete(self, task_id: str) -> bool:
        items=self._read()
        for item in items:
            if item.get("id")==task_id: item["completed"]=True; self._write(items); return True
        return False
    def delete(self, task_id: str) -> bool:
        items=self._read(); new=[x for x in items if x.get("id")!=task_id]
        changed=len(new)!=len(items); self._write(new); return changed
    def search(self, query: str):
        q=query.lower(); return [x for x in self._read() if q in x.get("title","").lower()]
