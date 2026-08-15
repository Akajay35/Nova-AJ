from core.planner import Planner
from core.tool_registry import Tool, ToolRegistry


def test_plan_build_and_summary():
    plan = Planner().build("finish project", ["research", "write", "review"])
    assert len(plan.steps) == 3
    assert plan.summary() == "0/3 steps completed for: finish project"


def test_planner_runs_only_registered_actions():
    planner = Planner()
    plan = planner.build("safe run", ["registered", "unregistered"])
    plan.steps[0].action = lambda: "done"
    planner.run(plan)
    assert plan.steps[0].status == "completed"
    assert plan.steps[1].status == "blocked"


def test_planner_binds_explicit_request_to_registered_tool():
    registry = ToolRegistry()
    registry.register(Tool("echo", "Echo text", lambda text: text))
    plan = Planner(registry).plan_tool_request("use echo hello Nova")
    assert plan.steps[0].tool_name == "echo"
    assert plan.steps[0].arguments == {"text": "hello Nova"}
    result = Planner(registry).run(plan)
    assert result.steps[0].status == "completed"
    assert result.steps[0].result == "hello Nova"


def test_planner_requires_confirmation_for_risky_tool():
    registry = ToolRegistry()
    registry.register(Tool("delete", "Deletes data", lambda text: "deleted", risk_level="high"))
    planner = Planner(registry)
    plan = planner.plan_tool_request("use delete old files")
    result = planner.run(plan)
    assert result.steps[0].status == "blocked"
    assert "confirmation" in result.steps[0].result.lower()


def test_planner_never_invents_unknown_tools():
    registry = ToolRegistry()
    planner = Planner(registry)
    plan = planner.plan_tool_request("use imaginary do something")
    assert plan.steps[0].status == "blocked"
    assert plan.steps[0].result == "Tool is not registered."
