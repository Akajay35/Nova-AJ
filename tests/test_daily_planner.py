from core.daily_planner import DailyPlanner

def test_daily_plan_prioritizes_open_tasks():
    tasks=[{"id":1,"title":"one","status":"open"},{"id":2,"title":"done","status":"completed"}]
    projects=[{"id":1,"name":"Nova","status":"active"}]
    p=DailyPlanner().build(tasks, projects)
    assert p["open_task_count"] == 1
    assert len(p["priorities"]) == 1
    assert len(p["active_projects"]) == 1
