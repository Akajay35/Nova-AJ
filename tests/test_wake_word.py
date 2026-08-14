from core.wake_word import WakeWordDetector

def test_wake_word_activation_and_strip():
    d=WakeWordDetector()
    assert d.detect("Nova, what is my plan?")
    assert d.strip_wake_word("Nova, what is my plan?") == "what is my plan?"
    assert d.is_stop("go to sleep")

def test_voice_loop_standby_activation_and_sleep():
    from core.voice_loop import VoiceLoop
    class TTS:
        def __init__(self): self.items=[]
        def speak(self, text): self.items.append(text)
    class Pipeline:
        def __init__(self): self.tts=TTS()
        def assistant(self, text): return "ok:" + text
    p=Pipeline(); loop=VoiceLoop(WakeWordDetector(), p)
    assert loop.handle_transcript("hello") == "standby"
    assert loop.handle_transcript("Nova") == "activated"
    assert loop.active
    assert loop.handle_transcript("tell me a joke") == "ok:tell me a joke"
    assert loop.handle_transcript("go to sleep") == "sleep"
    assert not loop.active
