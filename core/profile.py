from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

PROFILE_FILE = Path("data/profile.json")

class ProfileStore:
    """Small, explicit user profile store. Only values the user asks Nova to save belong here."""
    def __init__(self, path: str | Path = PROFILE_FILE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"preferences": {}, "goals": [], "projects": [], "notes": []})

    def _read(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def set_preference(self, key: str, value: str) -> None:
        data = self._read(); data.setdefault("preferences", {})[key.strip()] = value.strip()
        data["updated_at"] = datetime.now(timezone.utc).isoformat(); self._write(data)

    def add(self, category: str, text: str) -> None:
        data = self._read(); data.setdefault(category, []).append(text.strip())
        data["updated_at"] = datetime.now(timezone.utc).isoformat(); self._write(data)

    def remove(self, term: str) -> int:
        data = self._read(); removed = 0; t = term.lower()
        for category in ("goals", "projects", "notes"):
            before = len(data.get(category, [])); data[category] = [x for x in data.get(category, []) if t not in x.lower()]; removed += before - len(data[category])
        prefs = data.get("preferences", {})
        for key in list(prefs):
            if t in key.lower() or t in str(prefs[key]).lower(): del prefs[key]; removed += 1
        if removed: data["updated_at"] = datetime.now(timezone.utc).isoformat(); self._write(data)
        return removed

    def summary(self) -> dict:
        data = self._read(); return {"preferences": data.get("preferences", {}), "goals": data.get("goals", []), "projects": data.get("projects", []), "notes": data.get("notes", [])}
