from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class VoiceRuntimeResult:
    heard: str
    response: str
    activated: bool

class VoiceRuntime:
    """Coordinates wake-word activation, listening, assistant processing and speech."""
    def __init__(self, listener, pipeline, wake_word: str = "nova", speak: Callable[[str], object] | None = None):
        self.listener = listener
        self.pipeline = pipeline
        self.wake_word = wake_word.lower().strip()
        self.speak = speak

    def run_once(self) -> VoiceRuntimeResult:
        text = self.listener.listen()
        if not text:
            return VoiceRuntimeResult("", "", False)
        lowered = text.lower()
        if self.wake_word not in lowered:
            return VoiceRuntimeResult(text, "", False)
        command = lowered.split(self.wake_word, 1)[1].strip(" ,.!?:")
        if not command:
            return VoiceRuntimeResult(text, "", True)
        result = self.pipeline.process_once(command)
        if result.response and self.speak:
            self.speak(result.response)
        return VoiceRuntimeResult(text, result.response, True)
