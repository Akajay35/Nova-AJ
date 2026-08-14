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
