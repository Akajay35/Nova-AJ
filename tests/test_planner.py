from core.planner import Planner


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
