from core.agent_brain import AgentBrain

class FakeProvider:
    def __init__(self): self.calls = []
    def answer(self, prompt, context):
        self.calls.append((prompt, context))
        return "hello from provider"

def test_agent_brain_delegates_to_provider():
    provider = FakeProvider(); brain = AgentBrain(provider)
    history = [{"role": "user", "text": "hi"}]
    assert brain.respond("hello", history) == "hello from provider"
    assert provider.calls == [("hello", history)]
