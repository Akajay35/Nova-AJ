from __future__ import annotations
from dataclasses import dataclass

@dataclass
class VoiceControllerResult:
    activated: bool
    session_started: bool

class VoiceController:
    """Connects standby wake-word detection to the bounded voice session."""
    def __init__(self, wake_word: str, listener, session):
        self.wake_word = wake_word.strip().lower()
        self.listener = listener
        self.session = session

    def run_once(self) -> VoiceControllerResult:
        heard = self.listener.listen()
        if not heard or not heard.strip():
            return VoiceControllerResult(False, False)
        text = heard.strip().lower()
        if not text.startswith(self.wake_word):
            return VoiceControllerResult(False, False)
        self.session.run()
        return VoiceControllerResult(True, True)
