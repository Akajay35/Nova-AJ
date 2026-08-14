from core.skill_builder import SkillBuilder

def test_builder_rejects_invalid_python(tmp_path):
    b=SkillBuilder(str(tmp_path))
    result=b.build("demo", "def broken(:")
    assert not result.ok

def test_builder_prepares_valid_skill(tmp_path):
    b=SkillBuilder(str(tmp_path))
    result=b.build("demo", "def run():\n    return 'ok'\n")
    assert result.ok
    assert (tmp_path / "demo.py").exists()
