from __future__ import annotations

import pyttsx3

from config import TTS_RATE


class Speaker:
    """Text-to-speech output with safe console fallback and diagnostics."""

    def __init__(self):
        self.engine = None
        self.available = False
        self.status = "unavailable"
        self.error = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", TTS_RATE)
            self.available = True
            self.status = "ready"
        except Exception as exc:
            self.status = "initialization_error"
            self.error = type(exc).__name__

    def speak(self, text: str) -> bool:
        print(f"Nova AJ: {text}")
        if self.engine is None:
            return False
        try:
            self.engine.say(str(text))
            self.engine.runAndWait()
            self.available = True
            self.status = "ready"
            self.error = None
            return True
        except Exception as exc:
            self.available = False
            self.status = "speech_error"
            self.error = type(exc).__name__
            return False

    def health(self) -> dict[str, object]:
        return {
            "available": self.available,
            "status": self.status,
            "error": self.error,
            "rate": TTS_RATE,
        }
