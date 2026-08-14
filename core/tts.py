from __future__ import annotations

class TextToSpeech:
    """Optional local TTS adapter. Falls back to a dry-run when no engine is installed."""
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", rate)
            self._engine.setProperty("volume", volume)
        except Exception:
            self._engine = None

    @property
    def available(self) -> bool:
        return self._engine is not None

    def speak(self, text: str) -> bool:
        if not text or not self._engine:
            return False
        self._engine.say(text)
        self._engine.runAndWait()
        return True
