from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from config import PROPOSAL_DIR

class SkillGrowth:
    """Records missing capabilities as reviewable proposals; never executes generated code."""
    def __init__(self, directory: str = PROPOSAL_DIR):
        self.directory = Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
    def record_missing(self, request: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        path = self.directory / f"skill-{stamp}.json"
        payload = {"status":"proposed","request":request.strip(),"created_at":datetime.now(timezone.utc).isoformat(),"next_step":"Implement and test a skill, then enable it manually."}
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
