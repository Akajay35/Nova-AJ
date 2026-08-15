from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.system_health_endpoint import handle_system_health_request


class FakeQueue:
    def status(self):
        return {"health": "healthy", "counts": {"queued": 1}, "total": 1}


def test_system_health_reports_ci_readiness(tmp_path):
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "tests.yml").write_text(
        """name: Nova AJ tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
""",
        encoding="utf-8",
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")

    audit = NotificationQueueAudit(tmp_path / "audit.json")
    status, payload = handle_system_health_request(FakeQueue(), audit, "/api/system-health", tmp_path)

    assert status == 200
    assert payload["ci"]["workflow_present"] is True
    assert payload["ci"]["tests_present"] is True
    assert payload["ci"]["triggers"] == {
        "push_main": True,
        "pull_request_main": True,
        "manual_dispatch": True,
    }
    assert payload["ci"]["ready"] is True
    assert payload["ci"]["test_command"] == "python -m pytest -q"


def test_system_health_reports_missing_ci_configuration(tmp_path):
    audit = NotificationQueueAudit(tmp_path / "audit.json")
    status, payload = handle_system_health_request(FakeQueue(), audit, "/api/system-health", tmp_path)

    assert status == 200
    assert payload["ci"]["workflow_present"] is False
    assert payload["ci"]["tests_present"] is False
    assert payload["ci"]["ready"] is False
