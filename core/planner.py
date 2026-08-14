from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PlanStep:
    id: int
    title: str
    action: Callable[[], str] | None = None
    status: str = "pending"
    result: str | None = None


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
    """Creates and executes small, explicit plans; never executes arbitrary code."""

    def build(self, goal: str, steps: list[str]) -> Plan:
        return Plan(goal=goal, steps=[PlanStep(i + 1, title) for i, title in enumerate(steps)])

    def run(self, plan: Plan) -> Plan:
        for step in plan.steps:
            if step.status != "pending":
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
