from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class VoicePipelineResult:
    heard: str
    response: str

class VoicePipeline:
    """Connect STT, assistant processing, and TTS through injectable adapters."""
    def __init__(self, stt, assistant: Callable[[str], str], tts):
        self.stt = stt
        self.assistant = assistant
        self.tts = tts

    def process_once(self, audio: Optional[object] = None) -> VoicePipelineResult:
        heard = self.stt.transcribe(audio)
        if not heard.strip():
            return VoicePipelineResult(heard="", response="")
        response = self.assistant(heard)
        if response:
            self.tts.speak(response)
        return VoicePipelineResult(heard=heard, response=response)
