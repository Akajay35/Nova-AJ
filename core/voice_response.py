from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class VoiceResponse:
    text: str
    speak: bool = True

class VoiceResponseHandler:
    """Turns Nova results and reminder events into spoken responses."""
    def __init__(self, speak: Callable[[str], object] | None = None):
        self.speak = speak or (lambda text: None)

    def from_result(self, result) -> VoiceResponse:
        if result is None:
            text="I didn't get a command."
        elif isinstance(result, str):
            text=result
        elif isinstance(result, dict):
            status=result.get("status")
            messages={
                "blocked":"I can't perform that action without the required permission.",
                "proposal_created":"I found a missing capability and created a skill proposal for your approval.",
                "no_match":"I don't have a matching skill for that request yet.",
                "executed":"Done.",
                "created":"Done. I've created it.",
                "forgotten":"Done. I've forgotten it.",
                "unavailable":"That service isn't available yet.",
            }
            text=messages.get(status, f"The request finished with status: {status}.") if status else "The request was processed."
        else:
            text="The request was processed."
        self.speak(text)
        return VoiceResponse(text)

    def from_reminder(self, reminder: dict) -> VoiceResponse:
        text=f"Reminder: {reminder.get('text', 'You have a reminder.')}"
        self.speak(text)
        return VoiceResponse(text)
