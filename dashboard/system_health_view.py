from __future__ import annotations

from html import escape
from pathlib import Path

from core.notification_queue import NotificationQueue
from dashboard.ci_badge_status import ci_badge_status
from dashboard.ci_diagnostics import diagnose_ci
from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.queue_status_api import notification_queue_status


def system_health_snapshot(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    repo_root: str | Path = ".",
    workflow_url: str | None = None,
) -> dict:
    queue_status = notification_queue_status(queue)
    ci = diagnose_ci(repo_root)
    github_actions = ci_badge_status(workflow_url)
    events = audit.list()
    failed = sum(1 for event in events if event.get("success") is False)
    return {
        "queue": queue_status,
        "audit": {"total": len(events), "failed": failed},
        "ci": {**ci, "github_actions": github_actions},
    }


def render_system_health_view(
    queue: NotificationQueue,
    audit: NotificationQueueAudit,
    repo_root: str | Path = ".",
    workflow_url: str | None = None,
) -> str:
    data = system_health_snapshot(queue, audit, repo_root, workflow_url)
    queue_health = escape(str(data["queue"].get("health", "unknown")))
    ci_state = "ready" if data["ci"]["ready"] else "not-ready"
    github_state = escape(str(data["ci"]["github_actions"]["status"]))
    return (
        '<section class="nova-system-health" aria-label="Nova AJ system health">'
        '<h2>Nova AJ System Health</h2>'
        f'<p>Notification Queue: <strong>{queue_health}</strong></p>'
        f'<p>Security Audit Failures: <strong>{data["audit"]["failed"]}</strong></p>'
        f'<p>Automated Tests: <strong>{escape(ci_state)}</strong></p>'
        f'<p>GitHub Actions: <strong>{github_state}</strong></p>'
        '</section>'
    )
