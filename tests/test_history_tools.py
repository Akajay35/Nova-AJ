from core.conversation_history import ConversationHistory
from core.history_tools import history_handlers
from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry


def test_search_history_returns_matching_recent_turns(tmp_path):
    history = ConversationHistory(tmp_path / "history.json", limit=10)
    history.add("user", "We discussed football rankings")
    history.add("assistant", "I explained the ranking system")
    history.add("user", "We also discussed Excel")
    result = history_handlers(history)["search_history"]("football")
    assert len(result) == 1
    assert result[0]["role"] == "user"


def test_history_for_day_supports_today(tmp_path):
    history = ConversationHistory(tmp_path / "history.json", limit=10)
    history.add("user", "today conversation")
    result = history_handlers(history)["history_for_day"]("today")
    assert result[-1]["text"] == "today conversation"


def test_history_search_rejects_empty_term(tmp_path):
    history = ConversationHistory(tmp_path / "history.json")
    try:
        history_handlers(history)["search_history"]("   ")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("empty history search should fail")


def test_tool_intelligence_extracts_history_topic():
    registry = ToolRegistry()
    registry.register(Tool("search_history", "Search recent persistent conversations by words or topic", lambda **kwargs: kwargs))
    registry.register(Tool("history_for_day", "Show persistent conversations from today, yesterday, or a specific date", lambda **kwargs: kwargs))
    match = ToolIntelligence(registry).match("what did we discuss about football recently?")
    assert match.name == "search_history"
    assert match.arguments == {"term": "football"}


def test_tool_intelligence_extracts_yesterday_history():
    registry = ToolRegistry()
    registry.register(Tool("history_for_day", "Show persistent conversations from today, yesterday, or a specific date", lambda **kwargs: kwargs))
    match = ToolIntelligence(registry).match("what did we discuss yesterday?")
    assert match.name == "history_for_day"
    assert match.arguments == {"day": "yesterday"}


def test_search_history_ignores_malformed_timestamps(tmp_path):
    history = ConversationHistory(tmp_path / "history.json", limit=10)
    history.add("user", "valid football conversation")
    entries = history._read()
    entries.insert(0, {"role": "user", "text": "broken timestamp", "timestamp": "not-a-date"})
    history._write(entries)
    result = history_handlers(history)["search_history"]("football")
    assert len(result) == 1
    assert result[0]["text"] == "valid football conversation"
