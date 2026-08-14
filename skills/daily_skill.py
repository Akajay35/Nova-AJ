from core.base_skill import BaseSkill
from core.daily_planner import DailyPlanner

class DailySkill(BaseSkill):
    name="daily_planner"; description="Show a daily personal priority summary"; keywords=["daily plan","morning briefing","today's priorities","today priorities"]
    def handle(self, query: str, context=None) -> str:
        tasks = context.get("tasks", []) if context else []
        projects = context.get("projects", []) if context else []
        return DailyPlanner().summary(tasks, projects)
