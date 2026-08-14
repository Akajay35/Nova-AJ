from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class VoiceResponse:
    text: str
    speak: bool = True

class VoiceResponseHandler:
    """Turns reminder events into assistant responses and delegates speech to injected TTS."""
    def __init__(self, speak: Callable[[str], object] | None = None):
        self.speak = speak or (lambda text: None)

    def from_reminder(self, reminder: dict) -> VoiceResponse:
        text = f"Reminder: {reminder.get('text', 'You have a reminder.')}"
        self.speak(text)
        return VoiceResponse(text)
