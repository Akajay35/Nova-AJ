from __future__ import annotations

from dashboard.notification_queue_audit import NotificationQueueAudit


def audit_snapshot(audit: NotificationQueueAudit, limit: int = 100) -> dict:
    """Return a read-only, secret-free audit payload for the Control Center."""
    limit = max(1, min(500, int(limit)))
    events = audit.list()
    return {"total": len(events), "events": events[-limit:]}


def audit_events(audit: NotificationQueueAudit, success: str = "all", limit: int = 100) -> list[dict]:
    events = audit_snapshot(audit, limit)["events"]
    if success == "success":
        return [event for event in events if event.get("success") is True]
    if success == "failed":
        return [event for event in events if event.get("success") is False]
    return events
