from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class PersonalContext:
    """Unified local context for explicit profile data and bounded user-approved memory."""
    def __init__(self, path: str = "data/personal_context.json", max_events: int = 100, memory_store=None, profile_store=None):
        self.path = Path(path); self.max_events = max_events
        self.memory_store = memory_store; self.profile_store = profile_store
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({"profile": {}, "events": []})
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return {"profile": {}, "events": []}
    def _write(self, data): self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    def set(self, key, value):
        data=self._read(); data.setdefault("profile", {})[key.strip()]=value.strip(); self._write(data)
        if self.profile_store: self.profile_store.set(key, value)
    def get(self, key, default=None): return self.profile_store.get(key, default) if self.profile_store else self._read().get("profile", {}).get(key, default)
    def remember_event(self, text):
        data=self._read(); events=data.setdefault("events", []); events.append({"text":text.strip(),"created_at":datetime.now(timezone.utc).isoformat()}); data["events"]=events[-self.max_events:]; self._write(data)
    def search(self, query):
        results=[]
        if self.memory_store: results.extend(self.memory_store.search(query))
        q=query.lower().strip(); results.extend(e for e in self._read().get("events", []) if q in e.get("text","").lower())
        return results[:10]
    def snapshot(self): return {"profile": self.profile_store.summary() if self.profile_store else self._read().get("profile", {}), "events": self._read().get("events", [])[-self.max_events:]}
    def build_context(self, query): return {"profile": self.snapshot()["profile"], "relevant": self.search(query)}
    def as_text(self, query):
        context=self.build_context(query); lines=[]
        if context["profile"]:
            lines.append("User-approved profile:"); lines.extend(f"- {k}: {v}" for k,v in context["profile"].items())
        if context["relevant"]:
            lines.append("Relevant user-approved context:"); lines.extend(f"- {item.get('key', item.get('text',''))}: {item.get('value','') or item.get('text','')}" for item in context["relevant"])
        return "\n".join(lines)
