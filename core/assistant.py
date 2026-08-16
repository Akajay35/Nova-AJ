from __future__ import annotations

from .listener import VoiceListener
from .speaker import Speaker
from .skill_manager import SkillManager
from .skill_management import SkillManagement
from .skill_permissions import SkillPermissions
from .system_status import SystemStatus
from .startup_diagnostics import StartupDiagnostics
from .memory import MemoryStore
from .learning import SkillGrowth
from .ai_provider import AIProvider
from .conversation import ConversationContext
from .agent import Agent
from .agent_brain import AgentBrain
from .tool_registry import Tool, ToolRegistry
from .builtin_tools import builtin_handlers
from .web_tools import web_handlers
from .voice_session import VoiceSession
from .profile import ProfileStore
from .profile_tools import profile_handlers
from .assistant_router import AssistantRouter
from .health_check import HealthCheck
from config import ASSISTANT_NAME, WAKE_WORD, VOICE_MAX_TURNS


class NovaAssistant:
    """Main application facade coordinating voice, routing, skills, memory, learning and tools."""
    def __init__(self, router=None):
        self.listener = VoiceListener(); self.speaker = Speaker(); self.skills = SkillManager()
        self.skills.load()
        self.skill_permissions = SkillPermissions()
        self.skill_management = SkillManagement(self.skills, self.skill_permissions)
        self.memory = MemoryStore(); self.profile = ProfileStore(); self.learning = SkillGrowth()
        self.ai = AIProvider(); self.brain = AgentBrain(self.ai); self.conversation = ConversationContext(); self.tools = ToolRegistry()
        self._register_tools(); self.agent = Agent(self.tools); self.router = router or AssistantRouter()
        self.health = HealthCheck({"listener": self.listener, "speaker": self.speaker, "skills": self.skills, "memory": self.memory, "profile": self.profile, "learning": self.learning, "ai": self.ai, "brain": self.brain, "conversation": self.conversation, "tools": self.tools, "agent": self.agent, "router": self.router})
        self.system_status = SystemStatus(self)
        self.startup_report = StartupDiagnostics(self)
        self.voice_session = VoiceSession(self.listener, self.speaker, max_turns=VOICE_MAX_TURNS)

    def _register_tools(self) -> None:
        self.tools.register(Tool(name="list_skills", description="List installed assistant skills", handler=lambda: ", ".join(self.skills.names()) or "No skills installed."))
        self.tools.register(Tool(name="list_tools", description="List explicitly registered agent tools", handler=lambda: ", ".join(self.tools.names()) or "No tools registered."))
        self.tools.register(Tool(name="show_profile", description="Show the user's explicit saved profile and preferences", handler=lambda: str(self.profile.summary())))
        self.tools.register(Tool(name="show_memory", description="Show recent saved personal memories", handler=lambda: str(self.memory.recent(10))))
        self.tools.register(Tool(name="search_memory", description="Search saved personal memories", handler=lambda term: str(self.memory.search(term))))
        self.tools.register(Tool(name="remember", description="Save an explicit personal memory", handler=lambda text, kind="fact": self.memory.remember(text, kind)))
        self.tools.register(Tool(name="forget_memory", description="Forget a specific saved memory by id", handler=lambda memory_id: self.memory.forget(memory_id)))
        self.tools.register(Tool(name="forget_matching_memory", description="Forget saved memories matching text", handler=lambda term: self.memory.forget_matching(term)))
        self.tools.register(Tool(name="skill_status", description="Show active, quarantined, and failed skills", handler=lambda: str(self.skill_management.status())))
        self.tools.register(Tool(name="refresh_skills", description="Refresh the skill registry", handler=lambda: str(self.skill_management.refresh())))
        self.tools.register(Tool(name="system_status", description="Show read-only Nova system readiness and skill health", handler=lambda: self.system_status.summary()))
        self.tools.register(Tool(name="startup_diagnostics", description="Explain current startup readiness issues", handler=lambda: self.startup_report.summary()))
        self.tools.register(Tool(name="show_audit", description="Show recent Nova tool and confirmation audit events", handler=lambda: str(self.agent.audit.recent(20))))
        profiles = profile_handlers(self.profile)
        self.tools.register(Tool(name="set_preference", description="Save an explicit user preference such as language, voice, or response style", handler=profiles["set_preference"]))
        self.tools.register(Tool(name="add_goal", description="Save an explicit user goal", handler=profiles["add_goal"]))
        self.tools.register(Tool(name="add_project", description="Save an explicit user project", handler=profiles["add_project"]))
        self.tools.register(Tool(name="add_note", description="Save an explicit user profile note", handler=profiles["add_note"]))
        self.tools.register(Tool(name="remove_profile_item", description="Remove profile items matching text", handler=profiles["remove_profile_item"], risk_level="medium"))
        builtins = builtin_handlers()
        self.tools.register(Tool(name="current_time", description="Show the current UTC time", handler=builtins["current_time"]))
        self.tools.register(Tool(name="calculate", description="Calculate a basic arithmetic expression safely", handler=builtins["calculate"]))
        web = web_handlers()
        self.tools.register(Tool(name="web_search", description="Search the public web for factual information using Wikipedia", handler=web["web_search"]))

    def startup_diagnostics(self) -> dict[str, object]:
        return self.startup_report.run()

    @staticmethod
    def _is_confirmation(query: str) -> bool:
        return query.strip().lower() in {"yes", "y", "confirm", "do it", "go ahead", "okay", "ok"}

    @staticmethod
    def _is_cancellation(query: str) -> bool:
        return query.strip().lower() in {"no", "n", "cancel", "stop", "don't", "do not"}

    def handle(self, query: str) -> str:
        query = query.strip()
        if not query: return "I didn't catch that."
        self.conversation.add("user", query)
        if self.agent.confirmation.pending is not None:
            if self._is_confirmation(query):
                result = self.agent.confirm_pending(); answer = result.text
                self.conversation.add("assistant", answer); return answer
            if self._is_cancellation(query):
                result = self.agent.cancel_pending(); answer = result.text
                self.conversation.add("assistant", answer); return answer
        resolved_query = self.conversation.resolve(query)
        routed = self.router.route(resolved_query)
        if routed.intent not in {"chat", "learning"} and routed.response is not None:
            answer = str(routed.response)
        else:
            skill = self.skills.find(resolved_query)
            if skill:
                try: answer = skill.handle(resolved_query, {"memory": self.memory, "assistant": self, "health": self.health, "skill_management": self.skill_management})
                except Exception: answer = "That skill failed safely."
            else:
                tool_result = self.agent.execute_query(resolved_query)
                if tool_result.tool_name:
                    answer = tool_result.text
                    self.conversation.observe_tool_result(tool_result.tool_name, tool_result.text)
                else:
                    personal_context = {"profile": self.profile.summary(), "relevant_memory": self.memory.search(resolved_query)[:6]}
                    answer = self.brain.respond(resolved_query, self.conversation.recent(), personal_context)
                    if not answer:
                        proposal = self.learning.record_missing(resolved_query)
                        answer = f"I don't have that skill yet. I recorded a skill proposal at {proposal}."
        self.conversation.add("assistant", answer); return answer

    def refresh_skills(self) -> list[str]:
        self.skill_management.refresh(); return self.skills.names()

    def run(self):
        diagnostics = self.startup_diagnostics()
        if not diagnostics["ready"]:
            self.speaker.speak(self.startup_report.summary())
        else:
            self.speaker.speak(f"{ASSISTANT_NAME} is ready. Say {WAKE_WORD} to wake me.")
        while True:
            try:
                if not self.listener.wait_for_wake_word(): continue
                self.refresh_skills(); self.voice_session.run(self.handle)
            except KeyboardInterrupt: self.speaker.speak("Goodbye."); break
            except Exception: self.speaker.speak("I hit a recoverable error.")
