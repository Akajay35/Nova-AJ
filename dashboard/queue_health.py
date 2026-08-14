from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_view import queue_snapshot


def queue_health(queue: NotificationQueue) -> dict:
    snapshot = queue_snapshot(queue)
    counts = snapshot["counts"]
    failed = counts.get("failed", 0)
    pending = counts.get("pending", 0)
    total = snapshot["total"]
    if failed:
        state = "degraded"
    elif pending:
        state = "processing"
    else:
        state = "healthy"
    return {
        "state": state,
        "healthy": state == "healthy",
        "total": total,
        "queued": counts.get("queued", 0),
        "pending": pending,
        "delivered": counts.get("delivered", 0),
        "failed": failed,
    }
