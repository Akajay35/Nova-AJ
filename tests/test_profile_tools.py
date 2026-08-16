from core.profile import ProfileStore
from core.profile_tools import profile_handlers
from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def make_registry(profile):
    registry = ToolRegistry()
    handlers = profile_handlers(profile)
    for name, handler in handlers.items():
        registry.register(Tool(name=name, description=name.replace("_", " "), handler=handler))
    return registry


def test_profile_handlers_persist_preferences_and_items(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    handlers = profile_handlers(profile)

    assert handlers["set_preference"]("language", "Hindi") == "Saved preference: language = Hindi"
    assert handlers["add_goal"]("Build Nova AJ") == "Saved goal: Build Nova AJ"
    assert handlers["add_project"]("Nova-AJ") == "Saved project: Nova-AJ"
    assert handlers["add_note"]("Prefer concise replies") == "Saved note: Prefer concise replies"

    summary = profile.summary()
    assert summary["preferences"]["language"] == "Hindi"
    assert "Build Nova AJ" in summary["goals"]
    assert "Nova-AJ" in summary["projects"]
    assert "Prefer concise replies" in summary["notes"]


def test_tool_intelligence_extracts_preference_and_goal():
    profile = ProfileStore.__new__(ProfileStore)
    registry = make_registry(profile)
    intelligence = ToolIntelligence(registry)

    preference = intelligence.match("set my language to Hindi")
    assert preference.name == "set_preference"
    assert preference.arguments == {"key": "language", "value": "hindi"}

    goal = intelligence.match("my goal is build Nova AJ")
    assert goal.name == "add_goal"
    assert goal.arguments == {"text": "build Nova AJ"}
