from __future__ import annotations
import json
from pathlib import Path

REGISTRY_FILE = Path("data/skill_registry.json")

class SkillRegistry:
    """Local registry for skill metadata, capability discovery, and explicit enable/disable state."""
    def __init__(self, path: str = str(REGISTRY_FILE)):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({})
    def _read(self) -> dict:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {}
    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    def register(self, name: str, version: str = "1.0.0", enabled: bool = True, description: str = "", permissions: list[str] | None = None, security_status: str = "unknown") -> None:
        data=self._read(); data[name]={"version":version,"enabled":enabled,"description":description,"permissions":permissions or [],"security_status":security_status}; self._write(data)
    def set_enabled(self, name: str, enabled: bool) -> bool:
        data=self._read()
        if name not in data: return False
        data[name]["enabled"]=enabled; self._write(data); return True
    def enable(self, name: str) -> bool: return self.set_enabled(name, True)
    def disable(self, name: str) -> bool: return self.set_enabled(name, False)
    def remove(self, name: str) -> bool:
        data=self._read()
        if name not in data: return False
        del data[name]; self._write(data); return True
    def get(self, name: str) -> dict | None: return self._read().get(name)
    def list(self, enabled_only: bool = False) -> dict:
        data=self._read(); return {k:v for k,v in data.items() if v.get("enabled")} if enabled_only else data
    def available(self) -> dict: return self.list(enabled_only=True)
    def search(self, query: str) -> dict:
        q=query.lower(); return {k:v for k,v in self._read().items() if q in k.lower() or q in v.get("description","").lower()}
