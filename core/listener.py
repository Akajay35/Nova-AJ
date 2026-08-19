from __future__ import annotations

import speech_recognition as sr

from config import LANGUAGE, WAKE_WORD


class VoiceListener:
    """Microphone listener with safe, inspectable hardware/STT status."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.available = False
        self.status = "unavailable"
        self.error = None
        try:
            self.microphone = sr.Microphone()
            self.available = True
            self.status = "ready"
        except Exception as exc:
            self.error = type(exc).__name__

    def health(self) -> dict[str, str | bool | None]:
        return {
            "available": self.available,
            "status": self.status,
            "error": self.error,
            "language": LANGUAGE,
        }

    def listen(self) -> str:
        if self.microphone is None:
            return ""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
            text = self.recognizer.recognize_google(audio, language=LANGUAGE).strip()
            self.status = "ready"
            self.error = None
            return text
        except sr.WaitTimeoutError:
            self.status = "timeout"
            self.error = "WaitTimeoutError"
        except sr.UnknownValueError:
            self.status = "unrecognized"
            self.error = "UnknownValueError"
        except sr.RequestError:
            self.status = "stt_request_error"
            self.error = "RequestError"
        except Exception as exc:
            self.status = "listener_error"
            self.error = type(exc).__name__
        return ""

    def wait_for_wake_word(self) -> bool:
        return WAKE_WORD in self.listen().lower()
