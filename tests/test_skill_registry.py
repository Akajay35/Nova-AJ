from core.skill_registry import SkillRegistry

def test_registry_lifecycle(tmp_path):
    registry = SkillRegistry(str(tmp_path / "skills.json"))
    registry.register("demo", "1.0.0")
    assert registry.list()["demo"]["enabled"] is True
    assert registry.set_enabled("demo", False)
    assert registry.list()["demo"]["enabled"] is False
    assert registry.remove("demo")
    assert registry.list() == {}
