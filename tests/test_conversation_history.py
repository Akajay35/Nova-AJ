from core.conversation_history import ConversationHistory


def test_history_persists_and_is_bounded(tmp_path):
    path = tmp_path / "history.json"
    store = ConversationHistory(path, limit=3)
    store.add("user", "hello")
    store.add("assistant", "hi")
    store.add("user", "what time is it")
    store.add("assistant", "12:00")

    reloaded = ConversationHistory(path, limit=3)
    assert reloaded.count() == 3
    assert [item["role"] for item in reloaded.recent()] == ["assistant", "user", "assistant"]
    assert reloaded.recent()[0]["text"] == "hi"


def test_history_rejects_empty_text(tmp_path):
    store = ConversationHistory(tmp_path / "history.json")
    try:
        store.add("user", "   ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty conversation text should be rejected")


def test_history_clear(tmp_path):
    store = ConversationHistory(tmp_path / "history.json")
    store.add("user", "remember this conversation")
    store.clear()
    assert store.count() == 0
    assert store.recent() == []
