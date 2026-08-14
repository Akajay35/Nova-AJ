from __future__ import annotations
import json
from pathlib import Path

class ProfileStore:
    """Local, explicit user-profile preferences. Values are only stored when set by the caller."""
    def __init__(self, path: str = "data/profile.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({})
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {}
    def _write(self, data): self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def set(self, key: str, value: str) -> None:
        data=self._read(); data[key]=value; self._write(data)
    def get(self, key: str, default=None): return self._read().get(key, default)
    def remove(self, key: str) -> bool:
        data=self._read()
        if key not in data: return False
        del data[key]; self._write(data); return True
    def summary(self): return dict(self._read())
