from __future__ import annotations
import importlib
import inspect
from pathlib import Path
from .base_skill import BaseSkill

class SkillManager:
    def __init__(self, package: str = "skills"):
        self.package = package
        self.skills: list[BaseSkill] = []
        self.load_errors: list[dict[str, str]] = []
        self.discover()

    def discover(self) -> list[BaseSkill]:
        self.skills.clear()
        self.load_errors.clear()
        folder = Path(self.package.replace(".", "/"))
        for path in sorted(folder.glob("*_skill.py")):
            if path.name.startswith("_"):
                continue
            try:
                module = importlib.import_module(f"{self.package}.{path.stem}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseSkill) and obj is not BaseSkill and obj.__module__ == module.__name__:
                        self.skills.append(obj())
            except Exception as exc:
                self.load_errors.append({"skill": path.name, "error": type(exc).__name__, "message": str(exc)})
        return self.skills

    def find(self, query: str) -> BaseSkill | None:
        matches = [s for s in self.skills if s.matches(query)]
        return matches[0] if matches else None

    def names(self) -> list[str]:
        return [s.name for s in self.skills]

    def errors(self) -> list[dict[str, str]]:
        return list(self.load_errors)
