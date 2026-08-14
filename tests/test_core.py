from core.conversation import ConversationContext
from skills.calculator_skill import safe_eval


def test_calculator():
    assert safe_eval("2 + 3 * 4") == 14


def test_conversation_buffer():
    c = ConversationContext(limit=2)
    c.add("user", "hello")
    c.add("assistant", "hi")
    c.add("user", "next")
    assert len(c.recent()) == 2
    assert c.recent()[0]["text"] == "hi"
