from __future__ import annotations
import speech_recognition as sr
from config import WAKE_WORD, LANGUAGE

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer(); self.microphone = sr.Microphone()

    def listen(self) -> str:
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
        try: return self.recognizer.recognize_google(audio, language=LANGUAGE).strip()
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError): return ""

    def wait_for_wake_word(self) -> bool:
        text = self.listen().lower()
        return WAKE_WORD in text
