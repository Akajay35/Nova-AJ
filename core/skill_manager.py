from __future__ import annotations
import importlib
import inspect
from pathlib import Path
from .base_skill import BaseSkill
from .skill_security import scan_skill

class SkillManager:
    def __init__(self, package: str = "skills", quarantine_threshold: int = 2):
        self.package = package
        self.quarantine_threshold = max(1, quarantine_threshold)
        self.skills: list[BaseSkill] = []
        self.load_errors: list[dict[str, str]] = []
        self.quarantined: set[str] = set()
        self.failure_counts: dict[str, int] = {}
        self.discover()

    def discover(self) -> list[BaseSkill]:
        self.skills.clear(); self.load_errors.clear()
        folder = Path(self.package.replace(".", "/"))
        for path in sorted(folder.glob("*_skill.py")):
            if path.name.startswith("_") or path.name in self.quarantined: continue
            try:
                source = path.read_text(encoding="utf-8")
                report = scan_skill(source)
                if not report.safe:
                    self.load_errors.append({"skill": path.name, "error": "security_validation_failed", "message": "Skill blocked by static security validation.", "attempts": "0"})
                    self.quarantined.add(path.name)
                    continue
                module = importlib.import_module(f"{self.package}.{path.stem}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseSkill) and obj is not BaseSkill and obj.__module__ == module.__name__:
                        self.skills.append(obj())
                self.failure_counts.pop(path.name, None)
            except Exception as exc:
                count = self.failure_counts.get(path.name, 0) + 1
                self.failure_counts[path.name] = count
                self.load_errors.append({"skill": path.name, "error": type(exc).__name__, "message": "Skill failed to load.", "attempts": str(count)})
                if count >= self.quarantine_threshold: self.quarantined.add(path.name)
        return self.skills

    def find(self, query: str) -> BaseSkill | None:
        matches = [s for s in self.skills if s.matches(query)]
        return matches[0] if matches else None

    def names(self) -> list[str]: return [s.name for s in self.skills]
    def errors(self) -> list[dict[str, str]]: return list(self.load_errors)

    def quarantine(self, skill_filename: str) -> bool:
        if not skill_filename or not skill_filename.endswith("_skill.py"): return False
        self.quarantined.add(skill_filename)
        self.skills = [s for s in self.skills if getattr(s, "__module__", "").split(".")[-1] + ".py" != skill_filename]
        return True

    def unquarantine(self, skill_filename: str) -> bool:
        if skill_filename not in self.quarantined: return False
        self.quarantined.remove(skill_filename); self.failure_counts.pop(skill_filename, None)
        return True

    def quarantined_skills(self) -> list[str]: return sorted(self.quarantined)
