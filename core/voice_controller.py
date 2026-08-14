from __future__ import annotations
from dataclasses import dataclass

@dataclass
class VoiceControllerResult:
    activated: bool
    session_started: bool
    command: str | None = None
    route: object | None = None

class VoiceController:
    """Connects wake-word detection to Nova's command router and bounded voice session."""
    def __init__(self, wake_word: str, listener, session, router=None):
        self.wake_word = wake_word.strip().lower()
        self.listener = listener
        self.session = session
        self.router = router

    def run_once(self) -> VoiceControllerResult:
        heard = self.listener.listen()
        if not heard or not heard.strip():
            return VoiceControllerResult(False, False)
        text = heard.strip()
        lower = text.lower()
        if not lower.startswith(self.wake_word):
            return VoiceControllerResult(False, False)
        command = text[len(self.wake_word):].strip(" ,:.-")
        route = self.router.route(command) if self.router and command else None
        self.session.run()
        return VoiceControllerResult(True, True, command or None, route)
