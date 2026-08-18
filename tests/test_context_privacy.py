from core.context_privacy import ContextPrivacy


def test_privacy_allowlist_removes_unknown_profile_fields():
    context = {
        "profile": {
            "name": "Ajay",
            "preferences": {"language": "Hindi"},
            "email": "private@example.com",
            "phone": "+91-9999999999",
            "secret_token": "do-not-share",
        },
        "relevant_memories": [],
        "relevant_conversations": [],
    }

    result = ContextPrivacy().sanitize(context)

    assert result["profile"] == {
        "name": "Ajay",
        "preferences": {"language": "Hindi"},
    }
    assert "email" not in str(result)
    assert "phone" not in str(result)
    assert "secret_token" not in str(result)


def test_privacy_allowlist_removes_unknown_item_fields():
    context = {
        "profile": {},
        "relevant_memories": [
            {"text": "Nova project", "kind": "project", "secret": "hidden"}
        ],
        "relevant_conversations": [
            {"role": "user", "text": "continue Nova", "internal": "hidden"}
        ],
    }

    result = ContextPrivacy().sanitize(context)

    assert result["relevant_memories"] == [{"text": "Nova project", "kind": "project"}]
    assert result["relevant_conversations"] == [{"role": "user", "text": "continue Nova"}]
    assert "hidden" not in str(result)


def test_privacy_handles_invalid_context():
    result = ContextPrivacy().sanitize(None)
    assert result == {
        "profile": {},
        "relevant_memories": [],
        "relevant_conversations": [],
    }
