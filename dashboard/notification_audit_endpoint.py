from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.notification_queue_audit_api import audit_events


def handle_notification_audit_request(
    audit: NotificationQueueAudit,
    request_path: str,
) -> tuple[int, dict]:
    """Handle a read-only audit request without exposing credentials or mutating state."""
    parsed = urlparse(request_path)
    if parsed.path != "/api/notification-audit":
        return 404, {"error": "not found"}

    query = parse_qs(parsed.query)
    success = query.get("success", ["all"])[0]
    if success not in {"all", "success", "failed"}:
        return 400, {"error": "success must be all, success, or failed"}

    try:
        limit = int(query.get("limit", ["50"])[0])
    except ValueError:
        return 400, {"error": "limit must be an integer"}

    events = audit_events(audit, success=success, limit=max(1, min(200, limit)))
    return 200, {"total": len(events), "events": events}


def audit_response_json(audit: NotificationQueueAudit, request_path: str) -> tuple[int, bytes]:
    status, payload = handle_notification_audit_request(audit, request_path)
    return status, json.dumps(payload, ensure_ascii=False).encode("utf-8")
