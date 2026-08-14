"""
Handles microphone input: listens for the wake word, then captures the
command that follows and converts it to text.
"""

import speech_recognition as sr

import config


class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # One-time ambient noise calibration for more reliable recognition.
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen_for_wake_word(self) -> bool:
        """Blocks until it hears the configured wake word, then returns True."""
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source, timeout=None, phrase_time_limit=config.PHRASE_TIME_LIMIT
                )
                text = self.recognizer.recognize_google(audio).lower()
                return config.WAKE_WORD in text
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return False
            except sr.RequestError as e:
                print(f"[Listener] Speech recognition service error: {e}")
                return False

    def listen_for_command(self) -> str:
        """Captures a single spoken command and returns it as text, or '' if unclear."""
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=config.LISTEN_TIMEOUT,
                    phrase_time_limit=config.PHRASE_TIME_LIMIT,
                )
                return self.recognizer.recognize_google(audio)
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return ""
            except sr.RequestError as e:
                print(f"[Listener] Speech recognition service error: {e}")
                return ""
