from __future__ import annotations
import json
from pathlib import Path

REGISTRY_FILE = Path("data/skill_registry.json")

class SkillRegistry:
    """Safe local registry for installed/disabled skill metadata."""
    def __init__(self, path: str = str(REGISTRY_FILE)):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({})

    def _read(self) -> dict:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {}

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def register(self, name: str, version: str = "1.0.0", enabled: bool = True) -> None:
        data = self._read(); data[name] = {"version": version, "enabled": enabled}; self._write(data)

    def set_enabled(self, name: str, enabled: bool) -> bool:
        data = self._read()
        if name not in data: return False
        data[name]["enabled"] = enabled; self._write(data); return True

    def remove(self, name: str) -> bool:
        data = self._read()
        if name not in data: return False
        del data[name]; self._write(data); return True

    def list(self) -> dict: return self._read()
