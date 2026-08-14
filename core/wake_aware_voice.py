from __future__ import annotations
from dataclasses import dataclass

@dataclass
class WakeAwareResult:
    state: str
    text: str = ""

class WakeAwareVoice:
    """Small state machine for wake-word-aware continuous voice sessions."""
    def __init__(self, wake_detector, voice_pipeline, sleep_phrases=None):
        self.wake_detector = wake_detector
        self.voice_pipeline = voice_pipeline
        self.sleep_phrases = {x.lower() for x in (sleep_phrases or ["go to sleep", "sleep nova", "stop listening"])}
        self.active = False

    def process(self, text: str) -> WakeAwareResult:
        value = text.strip()
        low = value.lower()
        if not self.active:
            if self.wake_detector.detect(value):
                self.active = True
                cleaned = self.wake_detector.remove_wake_word(value).strip()
                return WakeAwareResult("active", cleaned)
            return WakeAwareResult("standby", "")
        if low in self.sleep_phrases:
            self.active = False
            return WakeAwareResult("standby", "")
        return WakeAwareResult("active", value)
