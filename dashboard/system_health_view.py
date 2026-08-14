from __future__ import annotations

from html import escape
from pathlib import Path

from core.notification_queue import NotificationQueue
from dashboard.ci_status import ci_configuration_status
from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.queue_status_api import notification_queue_status


def system_health_snapshot(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    repo_root: str | Path = ".",
) -> dict:
    queue_status = notification_queue_status(queue)
    ci_status = ci_configuration_status(repo_root)
    audit_events = audit.list()
    failed_audits = sum(1 for event in audit_events if event.get("success") is False)
    return {
        "queue": queue_status,
        "audit": {"total": len(audit_events), "failed": failed_audits},
        "ci": ci_status,
    }


def render_system_health_view(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    repo_root: str | Path = ".",
) -> str:
    data = system_health_snapshot(queue, audit, repo_root)
    queue_health = escape(str(data["queue"].get("health", "unknown")))
    ci = escape(str(data["ci"].get("status", "unknown")))
    audit_failed = data["audit"]["failed"]
    return (
        '<section class="nova-system-health" aria-label="Nova AJ system health">'
        '<h2>Nova AJ System Health</h2>'
        f'<p>Notification Queue: <strong>{queue_health}</strong></p>'
        f'<p>Security Audit Failures: <strong>{audit_failed}</strong></p>'
        f'<p>Automated Tests: <strong>{ci}</strong></p>'
        '</section>'
    )
