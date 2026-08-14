from __future__ import annotations

from core.notification_queue import NotificationQueue


ALLOWED_ACTIONS = {"pending", "delivered", "failed", "retry", "remove"}


def apply_action(queue: NotificationQueue, item_id: str, action: str, error: str = "") -> dict:
    """Apply one validated queue action and return the updated item."""
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"unsupported notification action: {action}")
    if not item_id:
        raise ValueError("item_id is required")
    if action == "pending":
        return queue.mark_pending(item_id)
    if action == "delivered":
        return queue.mark_delivered(item_id)
    if action == "failed":
        return queue.mark_failed(item_id, error)
    if action == "retry":
        return queue.retry(item_id)
    return queue.remove(item_id)
