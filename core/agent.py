from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .confirmation_state import ConfirmationState
from .tool_intelligence import ToolIntelligence
from .tool_registry import ToolRegistry


@dataclass
class AgentResult:
    text: str
    tool_name: str | None = None
    requires_confirmation: bool = False


class Agent:
    """Bounded orchestration around explicitly registered tools."""

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools
        self.intelligence = ToolIntelligence(tools)
        self.confirmation = ConfirmationState()

    def plan(self, query: str) -> AgentResult:
        match = self.intelligence.match(query)
        if match.name is None:
            return AgentResult("No registered tool matches this request yet.")
        tool = self.tools.get(match.name)
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
            self.confirmation.set(tool.name, kwargs)
            return AgentResult(
                f"The {tool.name} action needs your confirmation before I run it.",
                tool_name=tool.name,
                requires_confirmation=True,
            )
        try:
            result = self.tools.call(tool.name, **kwargs)
            self.confirmation.clear()
            return AgentResult(str(result), tool_name=tool.name)
        except Exception as exc:
            self.confirmation.clear()
            return AgentResult(f"The tool failed safely: {exc}", tool_name=tool.name)

    def execute_query(self, query: str, *, confirm: bool = False) -> AgentResult:
        """Select, authorize, and execute a registered tool."""
        match = self.intelligence.match(query)
        if match.name is None:
            return AgentResult("I couldn't safely identify a registered tool for that request.")
        return self.execute(match.name, confirm=confirm, **match.arguments)

    def confirm_pending(self) -> AgentResult:
        """Execute the previously blocked risky action after explicit confirmation."""
        action = self.confirmation.take()
        if action is None:
            return AgentResult("There is no pending action to confirm.")
        return self.execute(action.tool_name, confirm=True, **action.arguments)

    def cancel_pending(self) -> AgentResult:
        action = self.confirmation.take()
        if action is None:
            return AgentResult("There is no pending action to cancel.")
        return AgentResult(f"Cancelled the pending {action.tool_name} action.", tool_name=action.tool_name)
