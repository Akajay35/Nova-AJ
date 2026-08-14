from __future__ import annotations

from .listener import VoiceListener
from .speaker import Speaker
from .skill_manager import SkillManager
from .memory import MemoryStore
from .learning import SkillGrowth
from .ai_provider import AIProvider
from .conversation import ConversationContext
from .agent import Agent
from .tool_registry import Tool, ToolRegistry
from config import ASSISTANT_NAME, WAKE_WORD


class NovaAssistant:
    def __init__(self):
        self.listener = VoiceListener()
        self.speaker = Speaker()
        self.skills = SkillManager()
        self.memory = MemoryStore()
        self.learning = SkillGrowth()
        self.ai = AIProvider()
        self.conversation = ConversationContext()
        self.tools = ToolRegistry()
        self._register_tools()
        self.agent = Agent(self.tools)

    def _register_tools(self) -> None:
        self.tools.register(Tool(
            name="list_skills",
            description="List installed assistant skills",
            handler=lambda: ", ".join(self.skills.names()) or "No skills installed.",
        ))
        self.tools.register(Tool(
            name="list_tools",
            description="List explicitly registered agent tools",
            handler=lambda: ", ".join(self.tools.names()) or "No tools registered.",
        ))

    def handle(self, query: str) -> str:
        query = query.strip()
        if not query:
            return "I didn't catch that."

        self.conversation.add("user", query)
        skill = self.skills.find(query)
        if skill:
            try:
                answer = skill.handle(query, {"memory": self.memory, "assistant": self})
            except Exception as exc:
                answer = f"That skill failed safely: {exc}"
        else:
            planned = self.agent.plan(query)
            if planned.tool_name or planned.text.startswith("Available tools:"):
                answer = planned.text
            else:
                answer = self.ai.answer(query, self.conversation.recent())
                if not answer:
                    proposal = self.learning.record_missing(query)
                    answer = f"I don't have that skill yet. I recorded a skill proposal at {proposal}."

        self.conversation.add("assistant", answer)
        return answer

    def refresh_skills(self) -> list[str]:
        self.skills.discover()
        return self.skills.names()

    def run(self):
        self.speaker.speak(f"{ASSISTANT_NAME} is ready. Say {WAKE_WORD} to wake me.")
        while True:
            try:
                if not self.listener.wait_for_wake_word():
                    continue
                self.speaker.speak("Yes?")
                command = self.listener.listen()
                if command.lower() in {"exit", "quit", "stop", "goodbye"}:
                    self.speaker.speak("Goodbye.")
                    break
                self.speaker.speak(self.handle(command))
            except KeyboardInterrupt:
                self.speaker.speak("Goodbye.")
                break
            except Exception as exc:
                self.speaker.speak(f"I hit a recoverable error: {exc}")
