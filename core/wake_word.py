from __future__ import annotations

class WakeWordDetector:
    """Small provider-neutral wake-word detector for transcribed input."""
    def __init__(self, wake_words=None, stop_words=None):
        self.wake_words = tuple(w.lower() for w in (wake_words or ("nova", "nova aj")))
        self.stop_words = tuple(w.lower() for w in (stop_words or ("go to sleep", "stop listening", "goodbye nova")))

    def detect(self, text: str) -> bool:
        value = text.strip().lower()
        return any(word in value for word in self.wake_words)

    def is_stop(self, text: str) -> bool:
        value = text.strip().lower()
        return any(word in value for word in self.stop_words)

    def strip_wake_word(self, text: str) -> str:
        value = text.strip()
        lower = value.lower()
        for word in self.wake_words:
            if lower.startswith(word):
                return value[len(word):].lstrip(" ,:.-")
        return value
