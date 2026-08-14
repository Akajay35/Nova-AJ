from __future__ import annotations
import json
from pathlib import Path

class SkillLoader:
    """Discovers declarative skill manifests without importing or executing arbitrary code."""
    def __init__(self, skills_dir: str = "skills", registry=None):
        self.skills_dir = Path(skills_dir)
        self.registry = registry

    def discover(self):
        found=[]
        if not self.skills_dir.exists():
            return found
        for manifest in sorted(self.skills_dir.glob("*/skill.json")):
            try:
                data=json.loads(manifest.read_text(encoding="utf-8"))
                name=str(data["name"]).strip()
                if not name or not isinstance(data.get("permissions", []), list):
                    continue
                found.append({"name":name,"version":str(data.get("version","1.0.0")),"description":str(data.get("description","")),"permissions":data.get("permissions",[]),"path":str(manifest.parent)})
            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return found

    def register_discovered(self):
        if self.registry is None:
            return self.discover()
        items=self.discover()
        for item in items:
            self.registry.register(item["name"], item["version"], True, item["description"], item["permissions"], "manifest_only")
        return items
