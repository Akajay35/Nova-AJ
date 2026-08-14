from __future__ import annotations

from core.notification_queue import NotificationQueue
from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.notification_queue_auth import authorize_queue_request
from dashboard.notification_queue_http_api import handle_queue_action


def handle_audited_queue_action(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    request_path: str,
    token: str | None,
    actor: str = "unknown",
) -> tuple[int, dict]:
    """Authorize, execute, and audit a queue-management request."""
    item_id = _query_value(request_path, "id")
    action = _query_value(request_path, "action")

    if not authorize_queue_request(token):
        audit.record(actor=actor, action=action or "unknown", item_id=item_id or "unknown", success=False, reason="unauthorized")
        return 401, {"error": "unauthorized"}

    try:
        status, payload = handle_queue_action(queue, request_path)
        audit.record(
            actor=actor,
            action=action or "unknown",
            item_id=item_id or "unknown",
            success=status < 400,
            reason="" if status < 400 else str(payload.get("error", "request failed")),
        )
        return status, payload
    except Exception as exc:
        audit.record(actor=actor, action=action or "unknown", item_id=item_id or "unknown", success=False, reason=str(exc))
        return 500, {"error": "queue action failed"}


def _query_value(path: str, key: str) -> str:
    from urllib.parse import parse_qs, urlparse

    return parse_qs(urlparse(path).query).get(key, [""])[0]
