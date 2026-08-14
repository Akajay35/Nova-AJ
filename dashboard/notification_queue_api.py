from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_view import queue_snapshot


QUEUE = NotificationQueue("data/notification_queue.json")


def get_queue_snapshot(status: str = "all") -> dict:
    """Return a stable dashboard payload for the requested queue status."""
    status = str(status or "all").lower()
    allowed = {"all", "queued", "pending", "delivered", "failed"}
    if status not in allowed:
        status = "all"
    if status == "all":
        return queue_snapshot(QUEUE)

    items = QUEUE.list(status)
    counts = {"queued": 0, "pending": 0, "delivered": 0, "failed": 0}
    for item in items:
        state = str(item.get("status", "queued"))
        counts[state] = counts.get(state, 0) + 1
    return {
        "status": status,
        "counts": counts,
        "total": len(items),
        "items": items[-100:],
    }


def queue_health() -> dict:
    """Compact health information suitable for the main /api/status response."""
    snapshot = queue_snapshot(QUEUE)
    counts = snapshot["counts"]
    total = snapshot["total"]
    failed = counts.get("failed", 0)
    return {
        "total": total,
        "queued": counts.get("queued", 0),
        "pending": counts.get("pending", 0),
        "delivered": counts.get("delivered", 0),
        "failed": failed,
        "health": "attention" if failed else "healthy",
    }
