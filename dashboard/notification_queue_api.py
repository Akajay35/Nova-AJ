from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_view import queue_snapshot


QUEUE = NotificationQueue("data/notification_queue.json")


def get_queue_snapshot(status: str = "all") -> dict:
    if status == "all":
        return queue_snapshot(QUEUE)
    items = QUEUE.list(status)
    counts = {"queued": 0, "pending": 0, "delivered": 0, "failed": 0}
    for item in items:
        state = str(item.get("status", "queued"))
        counts[state] = counts.get(state, 0) + 1
    return {"counts": counts, "total": len(items), "items": items[-100:]}
