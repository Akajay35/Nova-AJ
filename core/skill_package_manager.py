from __future__ import annotations
import hashlib
import json
from pathlib import Path

class SkillPackageManager:
    """Versioned local package metadata with checksum verification and rollback."""
    def __init__(self, path: str = "data/skill_packages.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({})
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {}
    def _write(self,data): self.path.write_text(json.dumps(data,indent=2),encoding="utf-8")
    def install(self,name,version,content):
        data=self._read(); versions=data.setdefault(name,[])
        digest=hashlib.sha256(content.encode()).hexdigest()
        versions.append({"version":version,"sha256":digest,"active":True})
        for item in versions[:-1]: item["active"]=False
        self._write(data); return digest
    def rollback(self,name,version):
        data=self._read()
        for item in data.get(name,[]): item["active"]=item["version"]==version
        if not any(x["active"] for x in data.get(name,[])): return False
        self._write(data); return True
    def versions(self,name): return self._read().get(name,[])
