from core.agent import Agent
from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def build_registry():
    registry = ToolRegistry()
    registry.register(Tool("show_profile", "Show the user's explicit saved profile", lambda: "profile"))
    registry.register(Tool("search_memory", "Search saved personal memories", lambda term: f"found:{term}"))
    registry.register(Tool("remember", "Save an explicit personal memory", lambda text: f"saved:{text}"))
    registry.register(Tool("system_status", "Show read-only Nova system readiness and skill health", lambda: "ready"))
    registry.register(Tool("dangerous", "Delete external data", lambda: "deleted", risk_level="high"))
    return registry


def test_tool_intelligence_matches_synonyms():
    match = ToolIntelligence(build_registry()).match("can you display my account information")
    assert match.tool_name == "show_profile"


def test_tool_intelligence_extracts_memory_arguments():
    match = ToolIntelligence(build_registry()).match("please remember that I like football")
    assert match.tool_name == "remember"
    assert match.arguments == {"text": "I like football"}


def test_tool_intelligence_extracts_search_arguments():
    match = ToolIntelligence(build_registry()).match("find in memory football")
    assert match.tool_name == "search_memory"
    assert match.arguments == {"term": "football"}


def test_tool_intelligence_rejects_weak_match():
    match = ToolIntelligence(build_registry()).match("tell me something interesting")
    assert match.tool_name is None


def test_agent_uses_intelligence_for_natural_request():
    result = Agent(build_registry()).execute_query("can you show my profile")
    assert result.tool_name == "show_profile"
    assert result.text == "profile"


def test_agent_preserves_confirmation_for_risky_match():
    result = Agent(build_registry()).execute_query("delete external data")
    assert result.tool_name == "dangerous"
    assert result.requires_confirmation


def test_agent_can_execute_risky_match_after_confirmation():
    result = Agent(build_registry()).execute_query("delete external data", confirm=True)
    assert result.tool_name == "dangerous"
    assert result.text == "deleted"
