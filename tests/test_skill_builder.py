from core.skill_builder import SkillBuilder


def test_builder_rejects_invalid_python(tmp_path):
    b = SkillBuilder(str(tmp_path))
    result = b.build("demo", "def broken(:")
    assert not result.ok


def test_builder_rejects_dangerous_skill_source(tmp_path):
    b = SkillBuilder(str(tmp_path))
    result = b.build("demo", "import subprocess\nsubprocess.run(['echo', 'bad'])\n")
    assert not result.ok
    assert not (tmp_path / "demo.py").exists()


def test_builder_rejects_sensitive_calls(tmp_path):
    b = SkillBuilder(str(tmp_path))
    result = b.build("demo", "def run(value):\n    return eval(value)\n")
    assert not result.ok
    assert not (tmp_path / "demo.py").exists()


def test_builder_prepares_valid_skill(tmp_path):
    b = SkillBuilder(str(tmp_path))
    result = b.build("demo", "def run():\n    return 'ok'\n")
    assert result.ok
    assert (tmp_path / "demo.py").exists()
