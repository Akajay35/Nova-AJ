from __future__ import annotations

class SkillRouter:
    """Selects the best enabled registered skill for a command, without executing it."""
    def __init__(self, matcher, registry):
        self.matcher=matcher; self.registry=registry

    def select(self, text: str):
        matches=self.matcher.match(text)
        for match in matches:
            name=match.get("name") if isinstance(match, dict) else None
            skill=self.registry.get(name) if name else None
            if skill and skill.get("enabled", False):
                return {"status":"selected", "skill":name, "match":match}
        return {"status":"no_match", "skill":None}
