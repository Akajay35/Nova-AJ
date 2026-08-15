from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def build_tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Tool("show_profile", "Show the user's explicit saved profile", lambda: "profile"))
    registry.register(Tool("list_skills", "List installed assistant skills", lambda: "skills"))
    registry.register(Tool("system_status", "Show read-only Nova system readiness and skill health", lambda: "status"))
    registry.register(Tool("remember", "Save an explicit personal memory", lambda text: text))
    registry.register(Tool("search_memory", "Search saved personal memories", lambda term: term))
    return registry


def test_matches_tool_from_description_not_exact_phrase():
    match = ToolIntelligence(build_tools()).match("could you show me the installed skills")
    assert match.name == "list_skills"


def test_matches_system_status_from_natural_language():
    match = ToolIntelligence(build_tools()).match("is Nova ready")
    assert match.name == "system_status"


def test_extracts_remember_argument():
    match = ToolIntelligence(build_tools()).match("please remember that I like football")
    assert match.name == "remember"
    assert match.arguments == {"text": "I like football"}


def test_extracts_memory_search_argument():
    match = ToolIntelligence(build_tools()).match("can you search my memory for football")
    assert match.name == "search_memory"
    assert match.arguments == {"term": "football"}


def test_rejects_ambiguous_match():
    registry = ToolRegistry()
    registry.register(Tool("alpha", "Show account information", lambda: "a"))
    registry.register(Tool("beta", "Show account information", lambda: "b"))
    assert ToolIntelligence(registry).match("show account information").name is None
