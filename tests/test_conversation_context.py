from core.conversation import ConversationContext


def test_resolves_follow_up_reference_from_explicit_subject():
    context = ConversationContext()
    context.add("user", "Search Lionel Messi")
    assert context.resolve("When was he born?") == "When was Lionel Messi born?"


def test_web_result_can_refresh_subject():
    context = ConversationContext()
    context.observe_tool_result(
        "web_search",
        "Lionel Messi: Argentine footballer\nSource: https://en.wikipedia.org/wiki/Lionel_Messi",
    )
    assert context.resolve("Where is he from?") == "Where is Lionel Messi from?"


def test_does_not_invent_context_for_unrelated_request():
    context = ConversationContext()
    context.add("user", "Search Lionel Messi")
    assert context.resolve("What is the weather?") == "What is the weather?"
