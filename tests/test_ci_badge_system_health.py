from dashboard.ci_badge_status import ci_badge_status
from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.system_health_view import system_health_snapshot


class FakeQueue:
    def status(self):
        return {"health": "healthy", "counts": {"queued": 0}, "total": 0}


def test_ci_badge_status_defaults_to_unknown():
    status = ci_badge_status()
    assert status["status"] == "unknown"
    assert status["source"] == "github-actions"


def test_ci_badge_status_rejects_invalid_url():
    status = ci_badge_status("not-a-url")
    assert status == {"status": "unknown", "workflow_url": None}


def test_system_health_includes_github_actions_status(tmp_path):
    audit = NotificationQueueAudit(tmp_path / "audit.json")
    payload = system_health_snapshot(
        FakeQueue(), audit, tmp_path,
        "https://github.com/Akajay35/Nova-AJ/actions/workflows/tests.yml",
    )
    assert payload["ci"]["github_actions"]["status"] == "unknown"
    assert payload["ci"]["github_actions"]["source"] == "github-actions"
    assert payload["ci"]["github_actions"]["workflow_url"].startswith("https://github.com/")
