import pytest

from core.tool_intelligence import ToolIntelligence
from core.tool_registry import Tool, ToolRegistry
from core.web_tools import _clean_snippet, web_search


def test_web_search_rejects_empty_query():
    with pytest.raises(ValueError):
        web_search("")


def test_web_search_rejects_long_query():
    with pytest.raises(ValueError):
        web_search("x" * 201)


def test_web_search_rejects_invalid_limit():
    with pytest.raises(ValueError):
        web_search("Nova", limit="not-a-number")


def test_web_snippet_strips_markup():
    assert _clean_snippet('<span class="searchmatch">Nova</span> assistant') == "Nova assistant"


def test_tool_intelligence_extracts_web_query():
    registry = ToolRegistry()
    registry.register(Tool("web_search", "Search the public web for factual information using Wikipedia", web_search))
    match = ToolIntelligence(registry).match("search the web for Lionel Messi")
    assert match.name == "web_search"
    assert match.arguments == {"query": "Lionel Messi"}


def test_tool_intelligence_extracts_wikipedia_query():
    registry = ToolRegistry()
    registry.register(Tool("web_search", "Search the public web for factual information using Wikipedia", web_search))
    match = ToolIntelligence(registry).match("look up FIFA World Cup")
    assert match.name == "web_search"
    assert match.arguments == {"query": "FIFA World Cup"}
