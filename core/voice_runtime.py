from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class VoiceRuntimeResult:
    heard: str
    response: str
    activated: bool

class VoiceRuntime:
    """Coordinates wake-word activation with the existing assistant and TTS adapters."""
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
        position = lowered.find(self.wake_word)
        if position < 0:
            return VoiceRuntimeResult(text, "", False)
        command = text[position + len(self.wake_word):].strip(" ,.!?:")
        if not command:
            return VoiceRuntimeResult(text, "", True)
        response = self.pipeline.assistant(command)
        if response and self.speak:
            self.speak(response)
        return VoiceRuntimeResult(text, response, True)
