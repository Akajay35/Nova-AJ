from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class SkillLearning:
    """Safe skill-growth registry. It proposes and validates metadata; it never executes generated code."""
    def __init__(self, path: str = "data/skill_proposals.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write([])

    def _read(self) -> list[dict]:
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []

    def _write(self, items: list[dict]) -> None:
        self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def propose(self, request: str, reason: str) -> dict:
        items = self._read()
        proposal = {"id": len(items) + 1, "request": request.strip(), "reason": reason.strip(),
                    "status": "proposed", "created_at": datetime.now(timezone.utc).isoformat()}
        items.append(proposal); self._write(items); return proposal

    def list(self, status: str | None = None) -> list[dict]:
        items = self._read()
        return [x for x in items if status is None or x.get("status") == status]

    def validate(self, proposal_id: int) -> bool:
        for item in self._read():
            if item.get("id") == proposal_id:
                item["status"] = "validated"
                self._write(self._read())
                return True
        return False
