"""
Auto-discovers every skill in the skills/ folder and routes incoming queries
to whichever skill claims it can handle them.

This is the piece that makes the assistant's abilities grow automatically:
drop a new skill file in skills/, restart the assistant, and it's available.
No registration step, no editing this file.
"""

import importlib
import inspect
import pkgutil

from core.base_skill import BaseSkill


class SkillManager:
    def __init__(self, skills_package="skills"):
        self.skills_package = skills_package
        self.skills = []
        self.load_skills()

    def load_skills(self):
        """Import every module in the skills package and instantiate any BaseSkill subclasses found."""
        self.skills = []
        package = importlib.import_module(self.skills_package)

        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            # Skip sub-packages and files prefixed with "_" (e.g. the skill template,
            # which is meant to be copied, not loaded as-is).
            if is_pkg or module_name.startswith("_"):
                continue
            full_module_name = f"{self.skills_package}.{module_name}"
            module = importlib.import_module(full_module_name)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                    try:
                        self.skills.append(obj())
                    except Exception as e:
                        print(f"[SkillManager] Failed to load skill '{obj.__name__}': {e}")

        # Give any skill that wants a reference back to the manager (e.g. help_skill,
        # which needs to list every other loaded skill) access to it.
        for skill in self.skills:
            if hasattr(skill, "skill_manager"):
                skill.skill_manager = self

        print(f"[SkillManager] Loaded {len(self.skills)} skill(s): "
              f"{', '.join(s.name for s in self.skills)}")

    def route(self, query: str) -> str:
        """Find the first skill that claims it can handle the query and run it."""
        for skill in self.skills:
            if skill.can_handle(query):
                try:
                    return skill.handle(query)
                except Exception as e:
                    return f"I hit an error running the '{skill.name}' skill: {e}"

        return "I don't have a skill for that yet. You can add one in the skills folder."

    def list_skills(self) -> str:
        if not self.skills:
            return "I don't have any skills loaded."
        names = ", ".join(s.name for s in self.skills)
        return f"Here's what I can currently do: {names}."
