from core.skill_loader import SkillLoader
from core.skill_registry import SkillRegistry

def test_discovers_manifest(tmp_path):
    skill=tmp_path/"hello"; skill.mkdir(); (skill/"skill.json").write_text('{"name":"hello","version":"1.0.0","permissions":[]}', encoding="utf-8")
    registry=SkillRegistry(str(tmp_path/"registry.json")); found=SkillLoader(str(tmp_path), registry).register_discovered()
    assert found[0]["name"] == "hello"
    assert "hello" in registry.list()
