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
    """Small orchestration layer around explicitly registered tools.

    The agent never executes arbitrary model-generated Python. Tools must be
    registered by the application and high-risk tools can require confirmation.
    """

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def plan(self, query: str) -> AgentResult:
        text = query.lower().strip()
        if text in {"what tools do you have", "list tools", "show tools"}:
            names = ", ".join(self.tools.names()) or "none"
            return AgentResult(f"Available tools: {names}.")
        return AgentResult("No registered tool matches this request yet.")

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
