from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass
class Memory:
    key: str
    value: str
    category: str = "general"
    approved: bool = False
    created_at: str = ""

class MemoryStore:
    """Small local memory store; memories are opt-in and searchable."""
    def __init__(self, path: str = "data/memory.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, items): self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    def propose(self, key: str, value: str, category: str = "general") -> Memory:
        return Memory(key, value, category, False, datetime.now(timezone.utc).isoformat())
    def save(self, memory: Memory) -> bool:
        if not memory.approved: return False
        items=[x for x in self._read() if x.get("key") != memory.key]
        items.append(asdict(memory)); self._write(items); return True
    def approve_and_save(self, memory: Memory) -> bool:
        memory.approved=True; return self.save(memory)
    def search(self, query: str):
        q=query.lower(); return [x for x in self._read() if q in x.get("key","").lower() or q in x.get("value","").lower()]
    def forget(self, key: str) -> bool:
        items=self._read(); new=[x for x in items if x.get("key") != key]
        changed=len(new)!=len(items); self._write(new); return changed
