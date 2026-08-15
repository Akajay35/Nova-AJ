from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .tool_registry import ToolRegistry


@dataclass
class AgentResult:
    text: str
    tool_name: str | None = None
    requires_confirmation: bool = False


class Agent:
    """Bounded orchestration around explicitly registered tools.

    Natural-language matching is deterministic and conservative: Nova only
    selects a registered tool when a known intent has a clear match. It never
    executes arbitrary model-generated code.
    """

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def _match(self, query: str) -> tuple[str | None, dict[str, Any]]:
        text = query.strip()
        lowered = text.lower()

        if lowered in {"what tools do you have", "list tools", "show tools"}:
            return "__list_tools__", {}
        if lowered in {"show my profile", "show profile", "my profile"}:
            return "show_profile", {}
        if lowered in {"show my memory", "show memory", "what do you remember about me"}:
            return "show_memory", {}
        if lowered in {"list skills", "show skills", "what skills do you have"}:
            return "list_skills", {}
        if lowered in {"system status", "show system status", "status"}:
            return "system_status", {}
        if lowered in {"startup diagnostics", "diagnostics", "show startup diagnostics"}:
            return "startup_diagnostics", {}
        if lowered in {"refresh skills", "reload skills", "update skills"}:
            return "refresh_skills", {}

        # Match longer phrases before shorter prefixes so
        # "remember that ..." does not become "that ...".
        for prefix in ("remember that ", "remember ", "save this: "):
            if lowered.startswith(prefix):
                value = text[len(prefix):].strip()
                return ("remember", {"text": value}) if value else (None, {})

        for prefix in ("search my memory for ", "search memory for ", "find in memory "):
            if lowered.startswith(prefix):
                value = text[len(prefix):].strip()
                return ("search_memory", {"term": value}) if value else (None, {})

        for prefix in ("forget memory ", "delete memory ", "forget "):
            if lowered.startswith(prefix):
                value = text[len(prefix):].strip()
                if value and all(ch in "0123456789abcdef" for ch in value.lower()):
                    return "forget_memory", {"memory_id": value}
                if value:
                    return "forget_matching_memory", {"term": value}

        # Explicit requests remain supported for any registered tool.
        if lowered.startswith("use "):
            parts = text[4:].split(maxsplit=1)
            if len(parts) == 2 and self.tools.get(parts[0]):
                return parts[0], {"text": parts[1]}

        return None, {}

    def plan(self, query: str) -> AgentResult:
        text = query.strip()
        tool_name, arguments = self._match(text)
        if tool_name == "__list_tools__":
            names = ", ".join(self.tools.names()) or "none"
            return AgentResult(f"Available tools: {names}.")
        if tool_name is None:
            return AgentResult("No registered tool matches this request yet.")
        tool = self.tools.get(tool_name)
        if tool is None:
            return AgentResult("No registered tool matches this request yet.")
        return AgentResult(
            f"I can use {tool.name} to handle that request.",
            tool_name=tool.name,
            requires_confirmation=tool.risk_level != "low",
        )

    def execute(self, tool_name: str, *, confirm: bool = False, **kwargs: Any) -> AgentResult:
        tool = self.tools.get(tool_name)
        if tool is None:
            return AgentResult(f"I don't have a tool named {tool_name}.")
        if tool.risk_level != "low" and not confirm:
            return AgentResult(
                f"The {tool.name} action needs your confirmation before I run it.",
                tool_name=tool.name,
                requires_confirmation=True,
            )
        try:
            result = self.tools.call(tool.name, **kwargs)
            return AgentResult(str(result), tool_name=tool.name)
        except Exception as exc:
            return AgentResult(f"The tool failed safely: {exc}", tool_name=tool.name)

    def execute_query(self, query: str, *, confirm: bool = False) -> AgentResult:
        """Select and execute a clearly matched registered tool."""
        tool_name, arguments = self._match(query)
        if tool_name is None:
            return AgentResult("I couldn't safely identify a registered tool for that request.")
        if tool_name == "__list_tools__":
            return self.plan(query)
        return self.execute(tool_name, confirm=confirm, **arguments)
