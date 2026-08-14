from __future__ import annotations

DEFAULT_PERMISSIONS = {"memory", "web", "files", "browser", "system"}

class SkillPermissions:
    """Allowlist permissions for skills; sensitive permissions require explicit approval."""
    def __init__(self):
        self._permissions: dict[str, set[str]] = {}
        self._approved: set[tuple[str, str]] = set()

    def grant(self, skill: str, permission: str) -> bool:
        if permission not in DEFAULT_PERMISSIONS: return False
        self._permissions.setdefault(skill, set()).add(permission)
        return True

    def revoke(self, skill: str, permission: str) -> None:
        self._permissions.get(skill, set()).discard(permission)
        self._approved.discard((skill, permission))

    def approve_once(self, skill: str, permission: str) -> bool:
        if permission not in self._permissions.get(skill, set()): return False
        self._approved.add((skill, permission)); return True

    def can_use(self, skill: str, permission: str) -> bool:
        return permission in self._permissions.get(skill, set()) and (skill, permission) in self._approved

    def configured(self, skill: str) -> set[str]:
        return set(self._permissions.get(skill, set()))
