from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Task:
    id: int
    title: str
    status: str = "open"
    created_at: str = ""


class TaskManager:
    def __init__(self, path: str = "data/tasks.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, tasks: list[dict]) -> None:
        self.path.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, title: str) -> Task:
        tasks = self._read()
        next_id = max((int(x.get("id", 0)) for x in tasks), default=0) + 1
        task = Task(next_id, title.strip(), "open", datetime.now(timezone.utc).isoformat())
        tasks.append(asdict(task))
        self._write(tasks)
        return task

    def list_open(self) -> list[Task]:
        return [Task(**x) for x in self._read() if x.get("status") == "open"]

    def complete(self, task_id: int) -> bool:
        tasks = self._read()
        for task in tasks:
            if int(task.get("id", -1)) == task_id:
                task["status"] = "done"
                self._write(tasks)
                return True
        return False
