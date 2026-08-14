from core.voice_session import VoiceSession


class FakeSpeaker:
    def __init__(self): self.messages = []
    def speak(self, text): self.messages.append(text)


class FakeListener:
    def __init__(self, values): self.values = iter(values)
    def listen(self): return next(self.values)


def test_voice_session_handles_multiple_turns():
    speaker = FakeSpeaker()
    listener = FakeListener(["hello", "stop"])
    session = VoiceSession(listener, speaker, max_turns=5)
    session.run(lambda q: f"reply:{q}")
    assert "reply:hello" in speaker.messages
    assert speaker.messages[-1] == "Okay, going back to standby."


def test_voice_session_stops_after_idle_retries():
    speaker = FakeSpeaker()
    listener = FakeListener(["", ""])
    session = VoiceSession(listener, speaker, max_turns=5, idle_retries=2)
    session.run(lambda q: q)
    assert speaker.messages[-1] == "I'll wait for you to wake me again."
