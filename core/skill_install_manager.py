from __future__ import annotations
import json
from pathlib import Path

class SkillInstallManager:
    """Validates and stages local declarative skills; installation never enables execution automatically."""
    REQUIRED = ("name", "version", "description", "permissions")

    def __init__(self, skills_dir="skills", registry=None):
        self.skills_dir=Path(skills_dir); self.registry=registry

    def validate_manifest(self, manifest: dict):
        if not all(k in manifest for k in self.REQUIRED):
            return False, "missing_required_field"
        if not isinstance(manifest["name"], str) or not manifest["name"].strip():
            return False, "invalid_name"
        if not isinstance(manifest["permissions"], list):
            return False, "invalid_permissions"
        return True, "valid"

    def stage(self, manifest_path: str):
        path=Path(manifest_path)
        try:
            manifest=json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"status":"rejected", "reason":"invalid_manifest"}
        ok, reason=self.validate_manifest(manifest)
        if not ok:
            return {"status":"rejected", "reason":reason}
        if self.registry is not None:
            self.registry.register(manifest["name"], manifest["version"], False, manifest["description"], manifest["permissions"], "staged")
        return {"status":"staged", "name":manifest["name"], "version":manifest["version"], "enabled":False}
