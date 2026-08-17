from core.context_intelligence import ContextIntelligence
from core.context_resolver import ContextResolver
from core.conversation import ConversationContext
from core.conversation_history import ConversationHistory
from core.memory import MemoryStore
from core.profile import ProfileStore


def make_context(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    memory = MemoryStore(str(tmp_path / "memory.json"))
    history = ConversationHistory(tmp_path / "history.json", limit=20)
    profile.set_preference("language", "Hindi")
    memory.remember("User likes football")
    history.add("user", "We discussed football yesterday")
    resolver = ContextResolver(ConversationContext(), ContextIntelligence(profile, memory, history))
    return resolver


def test_profile_request_only_exposes_profile(tmp_path):
    context = make_context(tmp_path).context_for("what is my goal?")
    assert context["source"] == "profile"
    assert context["confidence"] == 0.95
    assert context["profile"]["preferences"]["language"] == "Hindi"
    assert context["relevant_memories"] == []
    assert context["relevant_conversations"] == []


def test_memory_request_only_exposes_matching_memory(tmp_path):
    context = make_context(tmp_path).context_for("what do you remember about football?")
    assert context["source"] == "memory"
    assert any("football" in item["text"].lower() for item in context["relevant_memories"])
    assert context["profile"] == {}
    assert context["relevant_conversations"] == []


def test_history_request_only_exposes_history(tmp_path):
    context = make_context(tmp_path).context_for("what did we discuss yesterday?")
    assert context["source"] == "history"
    assert context["profile"] == {}
    assert context["relevant_memories"] == []
    assert any("football" in item["text"].lower() for item in context["relevant_conversations"])


def test_unknown_request_does_not_expose_personal_context(tmp_path):
    context = make_context(tmp_path).context_for("tell me a joke")
    assert context["source"] == "none"
    assert context["confidence"] == 0.0
    assert context["profile"] == {}
    assert context["relevant_memories"] == []
    assert context["relevant_conversations"] == []


def test_follow_up_can_use_conversation_context(tmp_path):
    resolver = make_context(tmp_path)
    resolver.conversation.add("user", "search Lionel Messi")
    resolver.conversation.observe_tool_result("web_search", "Lionel Messi: footballer")
    context = resolver.context_for("when was he born?")
    assert context["source"] == "conversation"
    assert context["confidence"] == 1.0
    assert context["subject"] == "Lionel Messi"
