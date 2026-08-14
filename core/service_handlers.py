from __future__ import annotations

class ServiceHandlers:
    """Small adapters that connect the router to Nova's task and memory services."""
    def __init__(self, task_store=None, memory_store=None):
        self.task_store = task_store
        self.memory_store = memory_store

    def task(self, text: str):
        if self.task_store is None:
            return {"status": "unavailable", "message": "Task service is not configured."}
        return {"status": "received", "text": text}

    def memory(self, text: str):
        if self.memory_store is None:
            return {"status": "unavailable", "message": "Memory service is not configured."}
        return {"status": "received", "text": text}

    def skill(self, text: str):
        return {"status": "received", "text": text}

    def handlers(self):
        return {"task": self.task, "memory": self.memory, "skill": self.skill}
