from __future__ import annotations

import pyttsx3

from config import TTS_RATE


class Speaker:
    """Text-to-speech output that falls back to console output without an audio device."""

    def __init__(self):
        self.engine = None
        self.available = False
        self.error = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", TTS_RATE)
            self.available = True
        except Exception as exc:
            self.error = str(exc)

    def speak(self, text: str) -> None:
        print(f"Nova AJ: {text}")
        if self.engine is None:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            self.available = False
