from __future__ import annotations
from uuid import uuid4

class TaskMemoryCommands:
    """Concrete local commands. Callers should place permission/confirmation checks before mutations."""
    def __init__(self, task_store, memory_store, task_parser):
        self.tasks=task_store; self.memories=memory_store; self.parser=task_parser

    def create_task(self, text: str):
        parsed=self.parser.parse(text)
        task=self.tasks.add(__import__('core.task_store', fromlist=['Task']).Task(
            id=uuid4().hex, title=parsed.title, due_at=parsed.due_date, recurring=parsed.recurring
        ))
        return {"status":"created", "task":task.__dict__}

    def complete_task(self, task_id: str):
        return {"status":"completed" if self.tasks.complete(task_id) else "not_found", "task_id":task_id}

    def forget_memory(self, key: str):
        return {"status":"forgotten" if self.memories.forget(key) else "not_found", "key":key}
