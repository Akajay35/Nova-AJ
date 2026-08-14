from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .agent import Agent, AgentResult

@dataclass
class ToolLoopResult:
    text: str
    steps: int = 0
    needs_confirmation: bool = False

class ToolLoop:
    """Bounded tool execution loop. It only calls explicitly registered tools."""
    def __init__(self, agent: Agent, max_steps: int = 3):
        self.agent = agent
        self.max_steps = max(1, max_steps)

    def run(self, tool_name: str, confirm: bool = False, **kwargs: Any) -> ToolLoopResult:
        result: AgentResult = self.agent.execute(tool_name, confirm=confirm, **kwargs)
        return ToolLoopResult(result.text, steps=1, needs_confirmation=result.requires_confirmation)
