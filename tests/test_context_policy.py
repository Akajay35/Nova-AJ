from types import SimpleNamespace

from core.context_policy import ContextPolicy


def test_context_policy_bounds_each_context_source():
    snapshot = SimpleNamespace(
        profile={str(i): i for i in range(20)},
        memories=[{"text": f"memory {i}"} for i in range(10)],
        conversations=[{"text": f"conversation {i}"} for i in range(12)],
    )

    result = ContextPolicy(max_profile_fields=5, max_memories=3, max_conversations=4).apply(snapshot)

    assert len(result["profile"]) == 5
    assert len(result["relevant_memories"]) == 3
    assert len(result["relevant_conversations"]) == 4
    assert result["relevant_memories"][-1]["text"] == "memory 9"
    assert result["relevant_conversations"][-1]["text"] == "conversation 11"


def test_context_policy_clips_long_text():
    snapshot = SimpleNamespace(profile={}, memories=[{"text": "x" * 20}], conversations=[])

    result = ContextPolicy(max_text_chars=10).apply(snapshot)

    assert result["relevant_memories"][0]["text"] == "xxxxxxxxxx…"
