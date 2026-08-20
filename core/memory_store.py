from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass
class Memory:
    key: str
    value: str
    category: str = "general"
    approved: bool = False
    created_at: str = ""

class MemoryStore:
    MAX_KEY_LENGTH=128; MAX_VALUE_LENGTH=4096; MAX_CATEGORY_LENGTH=64; MAX_MEMORIES=500
    def __init__(self,path="data/memory.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        if not self.path.exists(): self._write([])
    def _read(self):
        try:
            data=json.loads(self.path.read_text(encoding="utf-8")); return data if isinstance(data,list) else []
        except (OSError,json.JSONDecodeError): return []
    def _write(self,items): self.path.write_text(json.dumps(items[-self.MAX_MEMORIES:],indent=2,ensure_ascii=False),encoding="utf-8")
    @classmethod
    def _validate(cls,memory):
        return isinstance(memory.key,str) and 0<len(memory.key)<=cls.MAX_KEY_LENGTH and isinstance(memory.value,str) and 0<len(memory.value)<=cls.MAX_VALUE_LENGTH and isinstance(memory.category,str) and 0<len(memory.category)<=cls.MAX_CATEGORY_LENGTH
    def propose(self,key,value,category="general"): return Memory(key,value,category,False,datetime.now(timezone.utc).isoformat())
    def save(self,memory):
        if not memory.approved or not self._validate(memory): return False
        items=[x for x in self._read() if x.get("key")!=memory.key]; items.append(asdict(memory)); self._write(items); return True
    def approve_and_save(self,memory): memory.approved=True; return self.save(memory)
    def remember(self,key,value,category="general",*,approved=False): return self.approve_and_save(self.propose(key,value,category)) if approved else False
    def search(self,query):
        if not isinstance(query,str) or not query.strip(): return []
        q=query.lower(); return [x for x in self._read() if q in str(x.get("key","")).lower() or q in str(x.get("value","")).lower()]
    def recall(self,key): return [Memory(**x) for x in self._read() if x.get("key")==key and x.get("approved",False)]
    def forget(self,key):
        items=self._read(); new=[x for x in items if x.get("key")!=key]; changed=len(new)!=len(items)
        if changed: self._write(new)
        return changed
