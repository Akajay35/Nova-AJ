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
    intelligence = ContextIntelligence(profile, memory, history)
    conversation = ConversationContext()
    return ContextResolver(conversation, intelligence), conversation, memory, history


def test_resolves_follow_up_reference_to_last_subject(tmp_path):
    resolver, conversation, _, _ = make_resolver(tmp_path)
    conversation.add("user", "search Lionel Messi")
    conversation.observe_tool_result("web_search", "Lionel Messi: footballer")

    result = resolver.resolve("when was he born?")

    assert result.query == "when was Lionel Messi born?"
    assert result.subject == "Lionel Messi"
    assert result.source == "conversation"


def test_classifies_memory_request(tmp_path):
    resolver, _, _, _ = make_resolver(tmp_path)
    result = resolver.resolve("what did I tell you about my memory?")
    assert result.source == "memory"


def test_classifies_history_request(tmp_path):
    resolver, _, _, _ = make_resolver(tmp_path)
    result = resolver.resolve("what did we discuss yesterday?")
    assert result.source == "history"


def test_classifies_profile_request(tmp_path):
    resolver, _, _, _ = make_resolver(tmp_path)
    result = resolver.resolve("what is my goal?")
    assert result.source == "profile"


def test_does_not_invent_reference_when_subject_is_unknown(tmp_path):
    resolver, _, _, _ = make_resolver(tmp_path)
    result = resolver.resolve("when was he born?")
    assert result.query == "when was he born?"
    assert result.subject is None
    assert result.source == "none"
