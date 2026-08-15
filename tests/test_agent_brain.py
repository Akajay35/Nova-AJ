from core.agent_brain import AgentBrain


class FakeProvider:
    def __init__(self):
        self.calls = []

    def answer(self, prompt, context, personal_context=None):
        self.calls.append((prompt, context, personal_context or {}))
        return "hello from provider"


def test_agent_brain_delegates_to_provider():
    provider = FakeProvider()
    brain = AgentBrain(provider)
    history = [{"role": "user", "text": "hi"}]
    personal_context = {"profile": {"name": "AJ"}, "relevant_memory": []}

    assert brain.respond("hello", history, personal_context) == "hello from provider"
    assert provider.calls == [("hello", history, personal_context)]
