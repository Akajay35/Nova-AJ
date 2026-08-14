from __future__ import annotations

from dataclasses import dataclass
from .listener import VoiceListener
from .speaker import Speaker

@dataclass
class VoiceSessionResult:
    turns: int
    ended: bool

class VoiceSession:
    """Bounded hands-free conversation routed through Nova's assistant brain."""
    def __init__(self, listener: VoiceListener, speaker: Speaker, max_turns: int = 8, idle_retries: int = 2):
        self.listener=listener; self.speaker=speaker; self.max_turns=max_turns; self.idle_retries=idle_retries

    def run(self, handle_query=None, router=None, responder=None) -> VoiceSessionResult:
        self.speaker.speak("I'm listening.")
        idle=0; turns=0
        for _ in range(self.max_turns):
            try: command=self.listener.listen()
            except Exception: command=""
            if not command:
                idle+=1
                if idle>=self.idle_retries:
                    self.speaker.speak("I'll wait for you to wake me again."); return VoiceSessionResult(turns, True)
                continue
            idle=0
            if command.lower().strip() in {"exit","quit","stop","goodbye","go to sleep","end session"}:
                self.speaker.speak("Okay, going back to standby."); return VoiceSessionResult(turns, True)
            if handle_query is not None:
                response=handle_query(command)
            elif router is not None:
                result=router.route(command).response
                response=responder.text(result) if responder is not None else result
            else:
                response=None
            turns+=1
            if response: self.speaker.speak(response)
        self.speaker.speak("Conversation limit reached. Say my wake word when you need me again.")
        return VoiceSessionResult(turns, True)
