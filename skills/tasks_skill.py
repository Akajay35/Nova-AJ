from core.base_skill import BaseSkill
from core.task_manager import TaskManager


class TasksSkill(BaseSkill):
    name = "tasks"
    description = "Create, list, and complete personal tasks."
    keywords = ["add task", "create task", "my tasks", "list tasks", "complete task"]

    def __init__(self):
        self.tasks = TaskManager()

    def matches(self, query: str) -> bool:
        q = query.lower().strip()
        return q.startswith(tuple(self.keywords))

    def handle(self, query: str, context=None) -> str:
        q = query.strip()
        low = q.lower()
        if low.startswith(("add task", "create task")):
            title = q.split(" ", 2)[-1].strip(" :,-")
            if not title:
                return "Tell me the task you want to add."
            task = self.tasks.add(title)
            return f"Added task {task.id}: {task.title}."
        if low.startswith(("my tasks", "list tasks")):
            tasks = self.tasks.list_open()
            if not tasks:
                return "You have no open tasks."
            return "Open tasks: " + "; ".join(f"{t.id}. {t.title}" for t in tasks)
        if low.startswith("complete task"):
            parts = q.split()
            try:
                task_id = int(parts[-1])
            except ValueError:
                return "Tell me the task number to complete."
            return "Task completed." if self.tasks.complete(task_id) else "I couldn't find that task."
        return "I can add, list, or complete tasks."
