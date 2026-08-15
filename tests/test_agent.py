from core.agent import Agent
from core.tool_registry import Tool, ToolRegistry


def test_low_risk_tool_executes():
    registry = ToolRegistry()
    registry.register(Tool("hello", "Returns hello", lambda: "hello"))
    result = Agent(registry).execute("hello")
    assert result.text == "hello"
    assert not result.requires_confirmation


def test_high_risk_tool_requires_confirmation():
    registry = ToolRegistry()
    registry.register(Tool("delete", "Deletes data", lambda: "deleted", risk_level="high"))
    result = Agent(registry).execute("delete")
    assert result.requires_confirmation
    assert "confirmation" in result.text.lower()


def build_agent():
    registry = ToolRegistry()
    registry.register(Tool("show_profile", "Show profile", lambda: "profile"))
    registry.register(Tool("search_memory", "Search memory", lambda term: f"found:{term}"))
    registry.register(Tool("remember", "Save memory", lambda text: f"saved:{text}"))
    return Agent(registry)


def test_agent_selects_tool_from_natural_language():
    result = build_agent().plan("show my profile")
    assert result.tool_name == "show_profile"
    assert not result.requires_confirmation


def test_agent_executes_natural_language_memory_search():
    result = build_agent().execute_query("search my memory for football")
    assert result.tool_name == "search_memory"
    assert result.text == "found:football"


def test_agent_saves_memory_from_natural_language():
    result = build_agent().execute_query("remember that I like football")
    assert result.tool_name == "remember"
    assert result.text == "saved:I like football"


def test_agent_keeps_unknown_requests_blocked():
    result = build_agent().execute_query("send an email to someone")
    assert result.tool_name is None
    assert "couldn't safely identify" in result.text
