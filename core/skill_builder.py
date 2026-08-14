from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ast

@dataclass
class BuildResult:
    ok: bool
    message: str

class SkillBuilder:
    """Builds only supplied Python skill source and performs static validation."""
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def validate(self, source: str) -> BuildResult:
        try:
            ast.parse(source)
        except SyntaxError as exc:
            return BuildResult(False, f"Syntax error: {exc}")
        return BuildResult(True, "Static syntax check passed.")

    def build(self, name: str, source: str) -> BuildResult:
        if not name.replace("_", "").isalnum() or not name:
            return BuildResult(False, "Invalid skill name.")
        check = self.validate(source)
        if not check.ok:
            return check
        path = self.skills_dir / f"{name}.py"
        if path.exists():
            return BuildResult(False, "Skill already exists.")
        path.write_text(source, encoding="utf-8")
        return BuildResult(True, f"Skill source prepared at {path}.")
