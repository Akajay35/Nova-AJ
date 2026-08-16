import pytest

from core.builtin_tools import calculate, current_time
from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def test_calculate_basic_expression():
    assert calculate("2 + 3 * 4") == "14"


def test_calculate_parentheses_and_power():
    assert calculate("(2 + 3) ** 2") == "25"


def test_calculate_rejects_code():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('echo unsafe')")


def test_current_time_is_utc_iso_timestamp():
    value = current_time()
    assert value.endswith("+00:00")
    assert "T" in value


def test_tool_intelligence_extracts_calculation():
    registry = ToolRegistry()
    registry.register(Tool("calculate", "Calculate a basic arithmetic expression safely", calculate))
    match = ToolIntelligence(registry).match("calculate 10 + 5 * 2")
    assert match.name == "calculate"
    assert match.arguments == {"expression": "10 + 5 * 2"}


def test_tool_intelligence_matches_current_time():
    registry = ToolRegistry()
    registry.register(Tool("current_time", "Show the current UTC time", current_time))
    match = ToolIntelligence(registry).match("what time is it")
    assert match.name == "current_time"
    assert match.arguments == {}
