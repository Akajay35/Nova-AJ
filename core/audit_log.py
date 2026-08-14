from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path

class AuditLog:
    """Append-only local activity log for important assistant decisions."""
    def __init__(self, path: str = "data/audit_log.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, items): self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    def record(self, event: str, skill: str = "", action: str = "", decision: str = "", result: str = ""):
        items=self._read(); items.append({"timestamp":datetime.now(timezone.utc).isoformat(),"event":event,"skill":skill,"action":action,"decision":decision,"result":result}); self._write(items)
    def recent(self, limit: int = 20): return self._read()[-max(0, limit):]
