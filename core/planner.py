from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .tool_registry import ToolRegistry


@dataclass
class PlanStep:
    id: int
    title: str
    action: Callable[[], str] | None = None
    status: str = "pending"
    result: str | None = None
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass
class Plan:
    goal: str
    steps: list[PlanStep] = field(default_factory=list)

    def next_pending(self) -> PlanStep | None:
        return next((step for step in self.steps if step.status == "pending"), None)

    def summary(self) -> str:
        done = sum(step.status == "completed" for step in self.steps)
        return f"{done}/{len(self.steps)} steps completed for: {self.goal}"


class Planner:
    """Creates bounded plans and can bind them only to registered tools."""

    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools

    def build(self, goal: str, steps: list[str]) -> Plan:
        return Plan(goal=goal, steps=[PlanStep(i + 1, title) for i, title in enumerate(steps)])

    def plan_tool_request(self, query: str) -> Plan:
        """Create a one-step plan only for an explicitly named registered tool."""
        if self.tools is None:
            return Plan(query.strip(), [PlanStep(1, "No tool registry configured", status="blocked", result="Tool registry is unavailable.")])

        text = query.strip()
        if not text.lower().startswith("use "):
            return Plan(text, [PlanStep(1, "No safe tool match", status="blocked", result="Only explicit 'use <tool> <text>' requests are supported.")])

        parts = text[4:].split(maxsplit=1)
        if len(parts) != 2:
            return Plan(text, [PlanStep(1, "Invalid tool request", status="blocked", result="Provide a tool name and argument.")])

        name, argument = parts
        tool = self.tools.get(name)
        if tool is None:
            return Plan(text, [PlanStep(1, f"Unknown tool: {name}", status="blocked", result="Tool is not registered.")])

        return Plan(
            goal=text,
            steps=[
                PlanStep(
                    1,
                    f"Run {name}",
                    tool_name=name,
                    arguments={"text": argument},
                    requires_confirmation=tool.risk_level != "low",
                )
            ],
        )

    def run(self, plan: Plan, *, confirm: bool = False) -> Plan:
        for step in plan.steps:
            if step.status != "pending":
                continue
            if step.tool_name is not None:
                if self.tools is None:
                    step.status = "blocked"
                    step.result = "Tool registry is unavailable."
                    break
                tool = self.tools.get(step.tool_name)
                if tool is None:
                    step.status = "blocked"
                    step.result = "Tool is no longer registered."
                    break
                if tool.risk_level != "low" and not confirm:
                    step.status = "blocked"
                    step.result = "Confirmation required before this action."
                    break
                try:
                    step.result = str(self.tools.call(tool.name, **step.arguments))
                    step.status = "completed"
                except Exception as exc:
                    step.status = "failed"
                    step.result = f"Step failed safely: {exc}"
                    break
                continue

            if step.action is None:
                step.status = "blocked"
                step.result = "No registered action is attached to this step."
                continue
            try:
                step.result = str(step.action())
                step.status = "completed"
            except Exception as exc:
                step.status = "failed"
                step.result = f"Step failed safely: {exc}"
                break
        return plan
