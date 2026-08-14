from core.tts import TextToSpeech

def test_tts_adapter_is_safe_without_engine(monkeypatch):
    tts = TextToSpeech()
    assert isinstance(tts.available, bool)
    if not tts.available:
        assert tts.speak("hello") is False
