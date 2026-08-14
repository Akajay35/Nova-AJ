from core.continuous_voice import ContinuousVoice

class Mic:
    def __init__(self): self.i=0
    def listen(self):
        self.i += 1
        return b"audio"
class Pipeline:
    class R:
        heard="hello"; response="hi"
    def process_once(self, audio): return self.R()

def test_continuous_voice_is_bounded():
    session=ContinuousVoice(Mic(), Pipeline(), max_cycles=3)
    result=session.run()
    assert result.cycles == 3
    assert result.stopped is True
