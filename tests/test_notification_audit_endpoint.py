from __future__ import annotations

import json
from pathlib import Path

from dashboard.notification_audit_endpoint import audit_response_json, handle_notification_audit_request
from dashboard.notification_queue_audit import NotificationQueueAudit


def make_audit(tmp_path: Path) -> NotificationQueueAudit:
    audit = NotificationQueueAudit(tmp_path / "audit.json")
    audit.record(actor="tester", action="retry", item_id="n1", success=True)
    audit.record(actor="tester", action="remove", item_id="n2", success=False, reason="not found")
    return audit


def test_all_events(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/notification-audit")
    assert status == 200
    assert payload["total"] == 2


def test_success_filter(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/notification-audit?success=success")
    assert status == 200
    assert payload["total"] == 1
    assert payload["events"][0]["success"] is True


def test_failed_filter(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/notification-audit?success=failed")
    assert status == 200
    assert payload["total"] == 1
    assert payload["events"][0]["success"] is False


def test_invalid_success_filter(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/notification-audit?success=bad")
    assert status == 400
    assert "success" in payload["error"]


def test_invalid_limit(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/notification-audit?limit=nope")
    assert status == 400
    assert "limit" in payload["error"]


def test_unknown_path(tmp_path: Path):
    status, payload = handle_notification_audit_request(make_audit(tmp_path), "/api/other")
    assert status == 404
    assert payload["error"] == "not found"


def test_json_response(tmp_path: Path):
    status, body = audit_response_json(make_audit(tmp_path), "/api/notification-audit?limit=1")
    assert status == 200
    payload = json.loads(body)
    assert payload["total"] == 1
    assert len(payload["events"]) == 1
