from __future__ import annotations

import json
from pathlib import Path


class PermissionManager:
    """Explicit per-skill permission store. Missing permissions default to deny."""

    def __init__(self, path: str = "data/permissions.json", config_path: str | Path | None = None):
        self.path = Path(config_path if config_path is not None else path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def configure(self, skill: str, permission: str) -> None:
        data = self._read()
        entry = data.setdefault(skill, {})
        entry.setdefault("configured", [])
        if permission not in entry["configured"]:
            entry["configured"].append(permission)
        self._write(data)

    def grant(self, skill: str, permission: str) -> None:
        data = self._read()
        entry = data.setdefault(skill, {})
        entry.setdefault("configured", [])
        entry.setdefault("granted", [])
        if permission not in entry["configured"]:
            entry["configured"].append(permission)
        if permission not in entry["granted"]:
            entry["granted"].append(permission)
        self._write(data)

    def revoke(self, skill: str, permission: str) -> bool:
        data = self._read()
        grants = data.get(skill, {}).get("granted", [])
        if permission not in grants:
            return False
        grants.remove(permission)
        self._write(data)
        return True

    def allowed(self, skill: str, permission: str) -> bool:
        return permission in self._read().get(skill, {}).get("granted", [])

    def configured(self, skill: str) -> set[str]:
        entry = self._read().get(skill, {})
        configured = entry.get("configured", [])
        # Existing stores that only have granted[] remain configured for compatibility.
        return {str(permission) for permission in configured} | {str(permission) for permission in entry.get("granted", [])}

    def can_use(self, skill: str, permission: str) -> bool:
        return self.allowed(skill, permission)
