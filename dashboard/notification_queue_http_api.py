from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_actions import apply_action


VALID_ACTIONS = {"pending", "delivered", "failed", "retry", "remove"}


def handle_queue_action(queue: NotificationQueue, request_path: str) -> tuple[int, dict]:
    """Framework-neutral HTTP handler for notification queue actions.

    Expected path:
      /api/notification-queue/action?id=<id>&action=<action>&error=<message>
    """
    parsed = urlparse(request_path)
    if parsed.path != "/api/notification-queue/action":
        return 404, {"error": "not found"}

    query = parse_qs(parsed.query)
    item_id = query.get("id", [""])[0].strip()
    action = query.get("action", [""])[0].strip().lower()
    error = query.get("error", [""])[0]

    if not item_id:
        return 400, {"error": "id is required"}
    if action not in VALID_ACTIONS:
        return 400, {"error": "invalid action", "allowed": sorted(VALID_ACTIONS)}

    try:
        item = apply_action(queue, item_id, action, error)
    except (KeyError, ValueError) as exc:
        return 400, {"error": str(exc)}

    return 200, {"ok": True, "action": action, "item": item}


def json_response(status: int, payload: dict) -> tuple[int, bytes]:
    return status, json.dumps(payload, ensure_ascii=False).encode("utf-8")
