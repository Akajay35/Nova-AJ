from core.skill_registry import SkillRegistry

def test_registry_discovers_capabilities(tmp_path):
    r=SkillRegistry(str(tmp_path/"skills.json"))
    r.register("calendar", "1.2.0", True, "Manage calendar events", ["calendar"], "passed")
    assert "calendar" in r.search("calendar")
    assert r.list(enabled_only=True)["calendar"]["version"] == "1.2.0"
    assert r.set_enabled("calendar", False)
    assert r.list(enabled_only=True) == {}
