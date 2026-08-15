from __future__ import annotations
import importlib
import importlib.util
import inspect
import json
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
        self._quarantine_file = self._state_path()
        self._load_quarantine_state()
        self.discover()

    def _skills_dir(self) -> Path:
        return Path(self.package.replace(".", "/"))

    def _state_path(self) -> Path:
        return self._skills_dir() / ".nova_quarantine.json"

    def _load_quarantine_state(self) -> None:
        try:
            data = json.loads(self._quarantine_file.read_text(encoding="utf-8"))
            entries = data.get("quarantined", [])
            if isinstance(entries, list):
                self.quarantined = {
                    name for name in entries
                    if isinstance(name, str) and name.endswith("_skill.py") and Path(name).name == name
                }
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            # Missing/corrupt state is non-fatal; source is still security-scanned
            # before every import, so a blocked skill cannot execute.
            self.quarantined = set()

    def _save_quarantine_state(self) -> None:
        self._quarantine_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "quarantined": sorted(self.quarantined)}
        temporary = self._quarantine_file.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self._quarantine_file)

    def _load_module(self, path: Path):
        """Load a skill from a package or an explicit skills directory."""
        package_path = self._skills_dir()
        if package_path.is_dir() and (Path(self.package).is_absolute() or "/" in self.package or "\\" in self.package):
            module_name = f"_nova_skill_{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load skill module: {path.name}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return importlib.import_module(f"{self.package}.{path.stem}")

    def discover(self) -> list[BaseSkill]:
        self.skills.clear(); self.load_errors.clear()
        folder = self._skills_dir()
        for path in sorted(folder.glob("*_skill.py")):
            if path.name.startswith("_") or path.name in self.quarantined: continue
            try:
                source = path.read_text(encoding="utf-8")
                report = scan_skill(source)
                if not report.safe:
                    self.load_errors.append({"skill": path.name, "error": "security_validation_failed", "message": "Skill blocked by static security validation.", "attempts": "0"})
                    self.quarantined.add(path.name)
                    self._save_quarantine_state()
                    continue
                module = self._load_module(path)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseSkill) and obj is not BaseSkill and obj.__module__ == module.__name__:
                        self.skills.append(obj())
                self.failure_counts.pop(path.name, None)
            except Exception as exc:
                count = self.failure_counts.get(path.name, 0) + 1
                self.failure_counts[path.name] = count
                self.load_errors.append({"skill": path.name, "error": type(exc).__name__, "message": "Skill failed to load.", "attempts": str(count)})
                if count >= self.quarantine_threshold:
                    self.quarantined.add(path.name)
                    self._save_quarantine_state()
        return self.skills

    def find(self, query: str) -> BaseSkill | None:
        matches = [s for s in self.skills if s.matches(query)]
        return matches[0] if matches else None

    def names(self) -> list[str]: return [s.name for s in self.skills]
    def errors(self) -> list[dict[str, str]]: return list(self.load_errors)

    def quarantine(self, skill_filename: str) -> bool:
        if not skill_filename or not skill_filename.endswith("_skill.py") or Path(skill_filename).name != skill_filename: return False
        self.quarantined.add(skill_filename)
        self.skills = [s for s in self.skills if getattr(s, "__module__", "").split(".")[-1] + ".py" != skill_filename]
        self._save_quarantine_state()
        return True

    def unquarantine(self, skill_filename: str) -> bool:
        if skill_filename not in self.quarantined: return False
        self.quarantined.remove(skill_filename); self.failure_counts.pop(skill_filename, None)
        self._save_quarantine_state()
        return True

    def quarantined_skills(self) -> list[str]: return sorted(self.quarantined)
