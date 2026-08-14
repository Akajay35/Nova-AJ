from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass
class SkillProposal:
    name: str
    description: str
    reason: str
    status: str = "pending"

class SkillLearningEngine:
    """Propose missing capabilities; never installs or executes code automatically."""
    def __init__(self, path: str = "data/skill_proposals.json"):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []
    def _write(self, items): self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    def propose(self, name: str, description: str, reason: str) -> SkillProposal:
        items=self._read(); existing=next((x for x in items if x["name"]==name and x["status"]=="pending"), None)
        if existing: return SkillProposal(**existing)
        proposal=SkillProposal(name, description, reason); items.append(asdict(proposal)); self._write(items); return proposal
    def list_pending(self): return [SkillProposal(**x) for x in self._read() if x.get("status")=="pending"]
    def approve(self, name: str) -> bool:
        items=self._read()
        for x in items:
            if x["name"]==name and x["status"]=="pending": x["status"]="approved"; self._write(items); return True
        return False
    def reject(self, name: str) -> bool:
        items=self._read()
        for x in items:
            if x["name"]==name and x["status"]=="pending": x["status"]="rejected"; self._write(items); return True
        return False
