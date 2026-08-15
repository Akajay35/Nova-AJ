from __future__ import annotations

import speech_recognition as sr

from config import LANGUAGE, WAKE_WORD


class VoiceListener:
    """Microphone listener that degrades safely when audio hardware is unavailable."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
            self.available = True
            self.error = None
        except Exception as exc:
            self.microphone = None
            self.available = False
            self.error = str(exc)

    def listen(self) -> str:
        if self.microphone is None:
            return ""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
            return self.recognizer.recognize_google(audio, language=LANGUAGE).strip()
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return ""
        except Exception:
            return ""

    def wait_for_wake_word(self) -> bool:
        return WAKE_WORD in self.listen().lower()
