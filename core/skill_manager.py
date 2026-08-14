from __future__ import annotations
import importlib
import inspect
from pathlib import Path
from .base_skill import BaseSkill

class SkillManager:
    def __init__(self, package: str = "skills"):
        self.package = package; self.skills: list[BaseSkill] = []; self.discover()

    def discover(self) -> list[BaseSkill]:
        self.skills.clear(); folder = Path(self.package.replace(".", "/"))
        for path in sorted(folder.glob("*_skill.py")):
            if path.name.startswith("_"): continue
            try:
                module = importlib.import_module(f"{self.package}.{path.stem}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseSkill) and obj is not BaseSkill and obj.__module__ == module.__name__:
                        self.skills.append(obj())
            except Exception as exc:
                print(f"[skill] skipped {path.name}: {exc}")
        return self.skills

    def find(self, query: str) -> BaseSkill | None:
        matches = [s for s in self.skills if s.matches(query)]
        return matches[0] if matches else None

    def names(self) -> list[str]: return [s.name for s in self.skills]
