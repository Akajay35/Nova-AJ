from core.context_intelligence import ContextIntelligence
from core.context_resolver import ContextResolver
from core.conversation import ConversationContext
from core.conversation_history import ConversationHistory
from core.memory import MemoryStore
from core.profile import ProfileStore


def make_resolver(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    memory = MemoryStore(str(tmp_path / "memory.json"))
    history = ConversationHistory(tmp_path / "history.json")
    return ContextResolver(conversation=ConversationContext(), intelligence=ContextIntelligence(profile, memory, history))


def test_context_resolution_has_confidence(tmp_path):
    resolver = make_resolver(tmp_path)
    result = resolver.resolve("what is my goal?")
    assert result.source == "profile"
    assert result.confidence == 0.95


def test_follow_up_resolution_is_high_confidence(tmp_path):
    resolver = make_resolver(tmp_path)
    resolver.conversation.add("user", "search Lionel Messi")
    resolver.conversation.observe_tool_result("web_search", "Lionel Messi: footballer")
    result = resolver.resolve("when was he born?")
    assert result.subject == "Lionel Messi"
    assert result.confidence == 1.0


def test_unknown_reference_has_zero_confidence(tmp_path):
    resolver = make_resolver(tmp_path)
    result = resolver.resolve("when was he born?")
    assert result.source == "none"
    assert result.subject is None
    assert result.confidence == 0.0


def test_hint_matching_does_not_use_substrings(tmp_path):
    resolver = make_resolver(tmp_path)
    result = resolver.resolve("recently I built a conversation tool")
    assert result.source == "history"
    assert result.confidence == 0.95
