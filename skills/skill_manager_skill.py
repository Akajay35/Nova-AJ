from core.base_skill import BaseSkill
from core.skill_registry import SkillRegistry

class SkillManagerSkill(BaseSkill):
    name = "skill_manager"
    description = "Manage enabled state of registered skills"
    keywords = ["list installed skills", "enable skill", "disable skill", "remove skill", "skill manager"]

    def handle(self, query: str, context=None) -> str:
        registry = context.get("skill_registry") if context else SkillRegistry()
        q = query.lower().strip()
        if q in {"list installed skills", "skill manager"} or "list installed skills" in q:
            items = registry.list()
            if not items: return "No skills are registered yet."
            return "Installed skills: " + ", ".join(f"{k} ({'enabled' if v.get('enabled') else 'disabled'})" for k,v in items.items())
        for action, enabled in (("enable skill", True), ("disable skill", False)):
            if action in q:
                name = q.split(action, 1)[1].strip()
                return (f"Skill {name} {'enabled' if enabled else 'disabled'}." if registry.set_enabled(name, enabled) else f"Skill {name} is not registered.")
        if "remove skill" in q:
            name = q.split("remove skill", 1)[1].strip()
            return f"Skill {name} removed." if registry.remove(name) else f"Skill {name} is not registered."
        return "I can list, enable, disable, or remove registered skills."
