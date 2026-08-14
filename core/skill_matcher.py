from __future__ import annotations
import re

class SkillMatcher:
    """Ranks enabled skills using simple token overlap against name and description."""
    def __init__(self, registry):
        self.registry = registry

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {t for t in re.findall(r"[a-z0-9_]+", text.lower()) if len(t) > 2}

    def match(self, command: str, limit: int = 3):
        query = self._tokens(command)
        ranked=[]
        for name, meta in self.registry.available().items():
            haystack=self._tokens(f"{name} {meta.get('description','')}")
            score=len(query & haystack)
            if score:
                ranked.append((score, name, meta))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [{"name":name,"score":score,"metadata":meta} for score,name,meta in ranked[:limit]]
