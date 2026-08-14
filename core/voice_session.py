from __future__ import annotations

from dataclasses import dataclass
from .listener import VoiceListener
from .speaker import Speaker


@dataclass
class VoiceSession:
    """A bounded hands-free conversation after the wake word."""
    listener: VoiceListener
    speaker: Speaker
    max_turns: int = 8
    idle_retries: int = 2

    def run(self, handle_query) -> None:
        self.speaker.speak("I'm listening.")
        idle = 0
        for _ in range(self.max_turns):
            try:
                command = self.listener.listen()
            except Exception:
                command = ""
            if not command:
                idle += 1
                if idle >= self.idle_retries:
                    self.speaker.speak("I'll wait for you to wake me again.")
                    return
                continue
            idle = 0
            if command.lower().strip() in {"exit", "quit", "stop", "goodbye", "go to sleep"}:
                self.speaker.speak("Okay, going back to standby.")
                return
            self.speaker.speak(handle_query(command))
        self.speaker.speak("Conversation limit reached. Say my wake word when you need me again.")
