from core.wake_aware_voice import WakeAwareVoice

class Wake:
    def detect(self, text): return text.lower().startswith("nova")
    def remove_wake_word(self, text): return text[4:].strip()
class Pipeline:
    pass

def test_wake_aware_state_machine():
    v=WakeAwareVoice(Wake(), Pipeline())
    assert v.process("hello there").state == "standby"
    r=v.process("Nova what is my plan")
    assert r.state == "active"
    assert r.text == "what is my plan"
    assert v.process("go to sleep").state == "standby"
