import pytest
from core.stt import SpeechToText

def test_stt_requires_provider():
    stt = SpeechToText()
    assert not stt.available
    with pytest.raises(RuntimeError):
        stt.transcribe(b"audio")

def test_stt_adapter():
    stt = SpeechToText(lambda audio: "  hello Nova  ")
    assert stt.available
    result = stt.transcribe(b"audio")
    assert result.text == "hello Nova"
