from __future__ import annotations

class SkillManagement:
    """Read-only facade for safe skill discovery and controlled recovery."""
    def __init__(self, manager):
        self.manager = manager

    def status(self) -> dict:
        return {
            "active": self.manager.names(),
            "quarantined": self.manager.quarantined_skills(),
            "errors": self.manager.errors(),
        }

    def refresh(self) -> dict:
        self.manager.discover()
        return self.status()

    def recover(self, filename: str) -> dict:
        if filename not in self.manager.quarantined_skills():
            return {"ok": False, "message": f"{filename} is not quarantined."}
        self.manager.unquarantine(filename)
        return {"ok": True, "message": f"{filename} released for the next refresh."}
