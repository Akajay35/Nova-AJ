from core.voice_pipeline import VoicePipeline

class STT:
    def transcribe(self, audio): return "hello Nova"
class TTS:
    def __init__(self): self.spoken=[]
    def speak(self, text): self.spoken.append(text)

def test_voice_pipeline_connects_stt_assistant_tts():
    tts=TTS(); pipeline=VoicePipeline(STT(), lambda text: "Hi!", tts)
    result=pipeline.process_once(b"audio")
    assert result.heard == "hello Nova"
    assert result.response == "Hi!"
    assert tts.spoken == ["Hi!"]
