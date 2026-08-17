from core.context_intelligence import ContextIntelligence
from core.conversation_history import ConversationHistory
from core.memory import MemoryStore
from core.profile import ProfileStore


def test_context_keeps_profile_memory_and_history_separate(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    memory = MemoryStore(str(tmp_path / "memory.json"))
    history = ConversationHistory(tmp_path / "history.json", limit=10)

    profile.set_preference("language", "Hindi")
    memory.remember("User is building Nova AJ")
    history.add("user", "We discussed Nova AJ testing")
    history.add("assistant", "The tests are passing")

    context = ContextIntelligence(profile, memory, history)
    snapshot = context.snapshot("Nova AJ")

    assert snapshot.profile["preferences"]["language"] == "Hindi"
    assert any("Nova AJ" in item["text"] for item in snapshot.memories)
    assert any("Nova AJ" in item["text"] for item in snapshot.conversations)
    assert all("language" not in item.get("text", "") for item in snapshot.memories)


def test_context_without_query_returns_recent_context(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    memory = MemoryStore(str(tmp_path / "memory.json"))
    history = ConversationHistory(tmp_path / "history.json", limit=10)
    memory.remember("Likes football")
    history.add("user", "Tell me about football")

    snapshot = ContextIntelligence(profile, memory, history).snapshot()

    assert snapshot.memories[-1]["text"] == "Likes football"
    assert snapshot.conversations[-1]["text"] == "Tell me about football"


def test_context_render_is_human_readable(tmp_path):
    profile = ProfileStore(tmp_path / "profile.json")
    memory = MemoryStore(str(tmp_path / "memory.json"))
    history = ConversationHistory(tmp_path / "history.json")
    memory.remember("Likes football")
    history.add("user", "Football plans")

    rendered = ContextIntelligence(profile, memory, history).render("football")

    assert "relevant_memories" in rendered
    assert "relevant_conversations" in rendered
    assert "Likes football" in rendered
    assert "Football plans" in rendered
