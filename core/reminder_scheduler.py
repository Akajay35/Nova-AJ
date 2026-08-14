from __future__ import annotations
import threading
import time
from datetime import datetime, timezone
from typing import Callable
from .reminders import ReminderStore

class ReminderScheduler:
    """Background reminder checker. Notification delivery is supplied by a callback."""
    def __init__(self, store: ReminderStore | None = None, interval_seconds: float = 30, on_due: Callable[[dict], None] | None = None):
        self.store=store or ReminderStore(); self.interval_seconds=max(1.0, interval_seconds); self.on_due=on_due or (lambda item: None); self._stop=threading.Event(); self._thread=None; self._seen=set()
    def check_once(self):
        due=self.store.due(datetime.now(timezone.utc))
        for item in due:
            if item["id"] not in self._seen:
                self._seen.add(item["id"]); self.on_due(item)
        return due
    def start(self):
        if self._thread and self._thread.is_alive(): return
        self._stop.clear(); self._thread=threading.Thread(target=self._run, daemon=True); self._thread.start()
    def _run(self):
        while not self._stop.is_set():
            self.check_once(); self._stop.wait(self.interval_seconds)
    def stop(self):
        self._stop.set()
        if self._thread: self._thread.join(timeout=self.interval_seconds + 1)
