import pyttsx3
from config import TTS_RATE

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init(); self.engine.setProperty("rate", TTS_RATE)
    def speak(self, text: str) -> None:
        print(f"Nova AJ: {text}"); self.engine.say(text); self.engine.runAndWait()
