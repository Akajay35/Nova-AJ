from __future__ import annotations

from .listener import VoiceListener
from .speaker import Speaker
from .skill_manager import SkillManager
from .skill_management import SkillManagement
from .skill_permissions import SkillPermissions
from .system_status import SystemStatus
from .memory import MemoryStore
from .learning import SkillGrowth
from .ai_provider import AIProvider
from .conversation import ConversationContext
from .agent import Agent
from .agent_brain import AgentBrain
from .tool_registry import Tool, ToolRegistry
from .voice_session import VoiceSession
from .profile import ProfileStore
from .assistant_router import AssistantRouter
from .health_check import HealthCheck
from config import ASSISTANT_NAME, WAKE_WORD, VOICE_MAX_TURNS

class NovaAssistant:
    """Main application facade coordinating voice, routing, skills, memory, learning and tools."""
    def __init__(self, router=None):
        self.listener = VoiceListener(); self.speaker = Speaker(); self.skills = SkillManager()
        self.skill_permissions = SkillPermissions()
        self.skill_management = SkillManagement(self.skills, self.skill_permissions)
        self.memory = MemoryStore(); self.profile = ProfileStore(); self.learning = SkillGrowth()
        self.ai = AIProvider(); self.brain = AgentBrain(self.ai); self.conversation = ConversationContext(); self.tools = ToolRegistry()
        self._register_tools(); self.agent = Agent(self.tools); self.router = router or AssistantRouter()
        self.health = HealthCheck({"listener": self.listener, "speaker": self.speaker, "skills": self.skills, "memory": self.memory, "profile": self.profile, "learning": self.learning, "ai": self.ai, "brain": self.brain, "conversation": self.conversation, "tools": self.tools, "agent": self.agent, "router": self.router})
        self.system_status = SystemStatus(self)
        self.voice_session = VoiceSession(self.listener, self.speaker, max_turns=VOICE_MAX_TURNS)

    def _register_tools(self) -> None:
        self.tools.register(Tool(name="list_skills", description="List installed assistant skills", handler=lambda: ", ".join(self.skills.names()) or "No skills installed."))
        self.tools.register(Tool(name="list_tools", description="List explicitly registered agent tools", handler=lambda: ", ".join(self.tools.names()) or "No tools registered."))
        self.tools.register(Tool(name="show_profile", description="Show the user's explicit saved profile", handler=lambda: str(self.profile.summary())))
        self.tools.register(Tool(name="skill_status", description="Show active, quarantined, and failed skills", handler=lambda: str(self.skill_management.status())))
        self.tools.register(Tool(name="refresh_skills", description="Refresh the skill registry", handler=lambda: str(self.skill_management.refresh())))
        self.tools.register(Tool(name="system_status", description="Show read-only Nova system readiness and skill health", handler=lambda: self.system_status.summary()))

    def startup_diagnostics(self) -> dict[str, object]:
        """Run read-only startup diagnostics before announcing readiness."""
        health = self.health.run()
        skill_status = self.skill_management.refresh()
        return {"ready": bool(health.get("ok")) and not bool(skill_status.get("errors")), "health": health, "skills": skill_status}

    def handle(self, query: str) -> str:
        query=query.strip()
        if not query: return "I didn't catch that."
        self.conversation.add("user", query); routed=self.router.route(query)
        if routed.intent not in {"chat", "learning"} and routed.response is not None: answer=str(routed.response)
        else:
            skill=self.skills.find(query)
            if skill:
                try: answer=skill.handle(query, {"memory": self.memory, "assistant": self, "health": self.health, "skill_management": self.skill_management})
                except Exception as exc: answer=f"That skill failed safely: {exc}"
            else:
                planned=self.agent.plan(query)
                if planned.tool_name or planned.text.startswith("Available tools:"): answer=planned.text
                else:
                    answer=self.brain.respond(query, self.conversation.recent())
                    if not answer:
                        proposal=self.learning.record_missing(query); answer=f"I don't have that skill yet. I recorded a skill proposal at {proposal}."
        self.conversation.add("assistant", answer); return answer

    def refresh_skills(self) -> list[str]:
        self.skill_management.refresh(); return self.skills.names()

    def run(self):
        diagnostics=self.startup_diagnostics()
        if not diagnostics["ready"]:
            self.speaker.speak("Nova startup diagnostics found an issue. System status needs attention.")
        else:
            self.speaker.speak(f"{ASSISTANT_NAME} is ready. Say {WAKE_WORD} to wake me.")
        while True:
            try:
                if not self.listener.wait_for_wake_word(): continue
                self.refresh_skills(); self.voice_session.run(self.handle)
            except KeyboardInterrupt: self.speaker.speak("Goodbye."); break
            except Exception as exc: self.speaker.speak(f"I hit a recoverable error: {exc}")
