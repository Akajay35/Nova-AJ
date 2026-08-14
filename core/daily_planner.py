from __future__ import annotations
from datetime import date

class DailyPlanner:
    """Create a simple daily priority view from tasks and projects."""
    def build(self, tasks=None, projects=None) -> dict:
        tasks = tasks or []
        projects = projects or []
        open_tasks = [t for t in tasks if t.get("status") not in {"completed", "done"}]
        active_projects = [p for p in projects if p.get("status") == "active"]
        return {
            "date": date.today().isoformat(),
            "priorities": open_tasks[:3],
            "active_projects": active_projects[:5],
            "open_task_count": len(open_tasks),
        }

    def summary(self, tasks=None, projects=None) -> str:
        plan = self.build(tasks, projects)
        return (f"Today: {plan['open_task_count']} open tasks and "
                f"{len(plan['active_projects'])} active projects. "
                f"Top priorities: {len(plan['priorities'])}.")
