"""
Handles all spoken output from the assistant using pyttsx3 (fully offline TTS).
"""

import pyttsx3

import config


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", config.TTS_RATE)
        self.engine.setProperty("volume", config.TTS_VOLUME)

    def say(self, text: str):
        print(f"[{config.ASSISTANT_NAME}] {text}")
        self.engine.say(text)
        self.engine.runAndWait()
