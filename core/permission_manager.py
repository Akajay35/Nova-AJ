from __future__ import annotations

import json
from pathlib import Path


class PermissionManager:
    """Explicit per-skill permission store. Missing permissions default to deny."""

    def __init__(self, path: str = "data/permissions.json"):
        self.path = Path(path)
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

    def grant(self, skill: str, permission: str) -> None:
        data = self._read()
        data.setdefault(skill, {}).setdefault("granted", [])
        if permission not in data[skill]["granted"]:
            data[skill]["granted"].append(permission)
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
        """Return permissions explicitly configured for a skill.

        The current permission model treats granted permissions as configured
        permissions. This keeps the guard fail-closed while remaining backward
        compatible with the existing JSON format.
        """
        grants = self._read().get(skill, {}).get("granted", [])
        return {str(permission) for permission in grants}

    def can_use(self, skill: str, permission: str) -> bool:
        return self.allowed(skill, permission)
