from pathlib import Path

from core.skill_manager import SkillManager


def _write_skill(folder: Path, marker: Path) -> None:
    (folder / "side_effect_skill.py").write_text(
        f'''from pathlib import Path
from core.base_skill import BaseSkill
Path({str(marker)!r}).write_text("executed", encoding="utf-8")

class SideEffectSkill(BaseSkill):
    name = "side-effect"
    keywords = ["side effect"]

    def handle(self, query, context=None):
        return "ok"
''',
        encoding="utf-8",
    )


def test_discovery_never_executes_skill_module(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    marker = tmp_path / "executed.txt"
    _write_skill(skills_dir, marker)

    manager = SkillManager(package=str(skills_dir), quarantine_threshold=2)

    discovered = manager.discover()

    assert [path.name for path in discovered] == ["side_effect_skill.py"]
    assert not marker.exists()
    assert manager.names() == []


def test_explicit_load_executes_only_after_security_scan(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    marker = tmp_path / "executed.txt"
    _write_skill(skills_dir, marker)

    manager = SkillManager(package=str(skills_dir))
    manager.discover()
    assert not marker.exists()

    manager.load()

    assert marker.read_text(encoding="utf-8") == "executed"
    assert manager.names() == ["side-effect"]
