from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class STTResult:
    text: str
    confidence: float | None = None

class SpeechToText:
    """Provider-neutral speech-to-text adapter. Microphone/provider code is injected."""
    def __init__(self, transcriber: Callable[[Any], str] | None = None):
        self.transcriber = transcriber

    @property
    def available(self) -> bool:
        return self.transcriber is not None

    def transcribe(self, audio: Any) -> STTResult:
        if self.transcriber is None:
            raise RuntimeError("No speech-to-text provider is configured.")
        text = self.transcriber(audio)
        if not isinstance(text, str):
            raise TypeError("Speech-to-text provider must return text.")
        return STTResult(text=text.strip())
