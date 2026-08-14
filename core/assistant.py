from __future__ import annotations
from .listener import VoiceListener
from .speaker import Speaker
from .skill_manager import SkillManager
from .memory import MemoryStore
from .learning import SkillGrowth
from .ai_provider import AIProvider
from config import ASSISTANT_NAME, WAKE_WORD

class NovaAssistant:
    def __init__(self):
        self.listener = VoiceListener(); self.speaker = Speaker(); self.skills = SkillManager()
        self.memory = MemoryStore(); self.learning = SkillGrowth(); self.ai = AIProvider()

    def handle(self, query: str) -> str:
        query = query.strip()
        if not query: return "I didn't catch that."
        skill = self.skills.find(query)
        if skill:
            try: return skill.handle(query, {"memory": self.memory, "assistant": self})
            except Exception as exc: return f"That skill failed safely: {exc}"
        answer = self.ai.answer(query)
        if answer: return answer
        proposal = self.learning.record_missing(query)
        return f"I don't have that skill yet. I recorded a skill proposal at {proposal}."

    def run(self):
        self.speaker.speak(f"{ASSISTANT_NAME} is ready. Say {WAKE_WORD} to wake me.")
        while True:
            try:
                if not self.listener.wait_for_wake_word(): continue
                self.speaker.speak("Yes?")
                command = self.listener.listen()
                if command.lower() in {"exit", "quit", "stop", "goodbye"}:
                    self.speaker.speak("Goodbye."); break
                self.speaker.speak(self.handle(command))
            except KeyboardInterrupt:
                self.speaker.speak("Goodbye."); break
            except Exception as exc:
                self.speaker.speak(f"I hit a recoverable error: {exc}")
