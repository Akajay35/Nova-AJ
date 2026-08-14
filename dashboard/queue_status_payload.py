from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.queue_health import queue_health
from dashboard.notification_queue_view import queue_snapshot


def queue_status_payload(queue: NotificationQueue) -> dict:
    """Return a compact, API-safe status payload for the main Nova status model."""
    snapshot = queue_snapshot(queue)
    return {
        "health": queue_health(queue),
        "counts": snapshot["counts"],
        "total": snapshot["total"],
        "recent": snapshot["items"][-20:],
    }
