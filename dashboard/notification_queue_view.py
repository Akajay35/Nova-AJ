from __future__ import annotations

from core.notification_queue import NotificationQueue


def queue_snapshot(queue: NotificationQueue) -> dict:
    items = queue.list()
    counts = {"queued": 0, "pending": 0, "delivered": 0, "failed": 0}
    for item in items:
        status = str(item.get("status", "queued"))
        counts[status] = counts.get(status, 0) + 1
    return {"counts": counts, "total": len(items), "items": items[-100:]}
