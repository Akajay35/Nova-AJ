from __future__ import annotations

class TaskMemoryService:
    """Executes only explicit, local task/memory operations; policy gates remain outside this adapter."""
    def __init__(self, task_store=None, memory_store=None, task_parser=None):
        self.task_store=task_store; self.memory_store=memory_store; self.task_parser=task_parser

    def handle_task(self, text: str):
        if not self.task_store or not self.task_parser:
            return {"status":"unavailable"}
        parsed=self.task_parser.parse(text)
        return {"status":"parsed", "title":parsed.title, "due_date":parsed.due_date, "recurring":parsed.recurring}

    def handle_memory(self, text: str):
        if not self.memory_store:
            return {"status":"unavailable"}
        proposal=self.memory_store.propose(text, text)
        return {"status":"proposal", "key":proposal.key, "value":proposal.value, "approved":False}
