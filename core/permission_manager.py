from __future__ import annotations
import json
from pathlib import Path

class PermissionManager:
    """Explicit per-skill permission store. Missing permissions default to ask/deny."""
    def __init__(self, path: str = "data/permissions.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({})
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {}
    def _write(self, data): self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def grant(self, skill: str, permission: str):
        data=self._read(); data.setdefault(skill, {}).setdefault("granted", [])
        if permission not in data[skill]["granted"]: data[skill]["granted"].append(permission)
        self._write(data)
    def revoke(self, skill: str, permission: str) -> bool:
        data=self._read(); grants=data.get(skill, {}).get("granted", [])
        if permission not in grants: return False
        grants.remove(permission); self._write(data); return True
    def allowed(self, skill: str, permission: str) -> bool:
        return permission in self._read().get(skill, {}).get("granted", [])
