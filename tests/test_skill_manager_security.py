from core.skill_manager import SkillManager
import json


def test_skill_manager_blocks_dangerous_skill_before_import(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "bad_skill.py").write_text(
        "import subprocess\n\nclass BadSkill:\n    pass\n",
        encoding="utf-8",
    )
    (skills_dir / "__init__.py").write_text("", encoding="utf-8")

    manager = SkillManager(str(skills_dir), quarantine_threshold=2)

    assert manager.names() == []
    assert "bad_skill.py" in manager.quarantined_skills()
    assert manager.errors()[0]["error"] == "security_validation_failed"
    assert manager.errors()[0]["message"] == "Skill blocked by static security validation."
    assert (skills_dir / ".nova_quarantine.json").exists()


def test_skill_manager_quarantine_survives_restart(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("", encoding="utf-8")
    (skills_dir / "bad_skill.py").write_text(
        "import subprocess\n\nclass BadSkill:\n    pass\n",
        encoding="utf-8",
    )

    first = SkillManager(str(skills_dir))
    assert "bad_skill.py" in first.quarantined_skills()

    second = SkillManager(str(skills_dir))
    assert "bad_skill.py" in second.quarantined_skills()
    assert second.names() == []


def test_quarantine_state_binds_to_source_hash(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("", encoding="utf-8")
    skill = skills_dir / "bad_skill.py"
    skill.write_text("import subprocess\n\nclass BadSkill:\n    pass\n", encoding="utf-8")

    manager = SkillManager(str(skills_dir))
    state = json.loads((skills_dir / ".nova_quarantine.json").read_text(encoding="utf-8"))
    assert state["version"] == 2
    assert len(state["quarantined"]["bad_skill.py"]) == 64

    # Changing the source invalidates the old quarantine entry. The new source
    # is nevertheless security-scanned before import.
    skill.write_text(
        "from core.base_skill import BaseSkill\n\n"
        "class SafeSkill(BaseSkill):\n"
        "    name = 'safe'\n"
        "    description = 'safe'\n"
        "    keywords = ['safe']\n"
        "    def handle(self, query, context=None):\n"
        "        return 'ok'\n",
        encoding="utf-8",
    )
    restarted = SkillManager(str(skills_dir))
    assert restarted.names() == ["safe"]
    assert "bad_skill.py" not in restarted.quarantined_skills()


def test_skill_manager_unquarantine_persists(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("", encoding="utf-8")
    (skills_dir / "bad_skill.py").write_text(
        "import subprocess\n\nclass BadSkill:\n    pass\n",
        encoding="utf-8",
    )

    manager = SkillManager(str(skills_dir))
    assert manager.unquarantine("bad_skill.py")

    restarted = SkillManager(str(skills_dir))
    assert "bad_skill.py" in restarted.quarantined_skills()


def test_skill_manager_loads_safe_skill(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "__init__.py").write_text("", encoding="utf-8")
    (skills_dir / "safe_skill.py").write_text(
        "from core.base_skill import BaseSkill\n\n"
        "class SafeSkill(BaseSkill):\n"
        "    name = 'safe'\n"
        "    description = 'safe'\n"
        "    keywords = ['safe']\n"
        "    def handle(self, query, context=None):\n"
        "        return 'ok'\n",
        encoding="utf-8",
    )

    manager = SkillManager(str(skills_dir))

    assert manager.names() == ["safe"]
