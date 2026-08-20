from __future__ import annotations
import json,re
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
_SAFE_NAME=re.compile(r"^[a-z0-9][a-z0-9_-]{1,48}$"); _ALLOWED_RISKS={"low","medium","high"}; _MAX_INSTRUCTION=4000; _MAX_STEPS=20
@dataclass(frozen=True)
class SkillDraft:
 name:str; description:str; trigger:str; steps:tuple[str,...]; risk_level:str="low"; required_permissions:tuple[str,...]=(); status:str="draft"; created_at:str=""
class SkillTrainer:
 def __init__(self,path:str|Path="data/trained_skills.json",storage_path:str|Path|None=None)->None:
  self.path=Path(storage_path if storage_path is not None else path); self.path.parent.mkdir(parents=True,exist_ok=True)
 def train(self,name,description,trigger,steps,*,risk_level="low",required_permissions=()):
  name=name.strip().lower(); description=description.strip(); trigger=trigger.strip(); normalized=tuple(s.strip() for s in steps if s and s.strip()); permissions=tuple(sorted({p.strip().lower() for p in required_permissions if p and p.strip()}))
  if not _SAFE_NAME.fullmatch(name): raise ValueError("invalid skill name")
  if not description or len(description)>_MAX_INSTRUCTION: raise ValueError("description must be 1-4000 characters")
  if not trigger or len(trigger)>300: raise ValueError("trigger must be 1-300 characters")
  if not normalized or len(normalized)>_MAX_STEPS: raise ValueError("skill must contain 1-20 steps")
  if any(len(s)>_MAX_INSTRUCTION for s in normalized): raise ValueError("skill step is too long")
  if risk_level not in _ALLOWED_RISKS: raise ValueError("invalid risk level")
  draft=SkillDraft(name,description,trigger,normalized,risk_level,permissions,"draft",datetime.now(timezone.utc).isoformat()); records=self._load(); records[name]=asdict(draft); self._save(records); return draft
 def approve(self,name): record=self._get(name); record["status"]="active"; self._save(self._all_with(name,record)); return self._to_draft(record)
 def disable(self,name): record=self._get(name); record["status"]="disabled"; self._save(self._all_with(name,record)); return self._to_draft(record)
 def get(self,name): return self._to_draft(self._get(name))
 def list(self,*,active_only=False):
  values=[self._to_draft(v) for v in self._load().values()]; return sorted([v for v in values if not active_only or v.status=="active"],key=lambda v:v.name)
 def test(self,name,query):
  draft=self.get(name); matched=draft.trigger.lower() in query.lower(); return {"name":draft.name,"status":draft.status,"matched":matched,"steps":list(draft.steps) if matched else []}
 def _load(self):
  if not self.path.exists(): return {}
  try: data=json.loads(self.path.read_text(encoding="utf-8")); return data if isinstance(data,dict) else {}
  except (OSError,json.JSONDecodeError): return {}
 def _save(self,records): self.path.write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
 def _get(self,name):
  name=name.strip().lower(); record=self._load().get(name)
  if not record: raise KeyError(f"skill not found: {name}")
  return record
 def _all_with(self,name,record): records=self._load(); records[name.strip().lower()]=record; return records
 @staticmethod
 def _to_draft(record): return SkillDraft(str(record["name"]),str(record["description"]),str(record["trigger"]),tuple(str(s) for s in record.get("steps",[])),str(record.get("risk_level","low")),tuple(str(p) for p in record.get("required_permissions",[])),str(record.get("status","draft")),str(record.get("created_at","")))
