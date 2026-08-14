from dashboard.notification_queue_audit import NotificationQueueAudit
from dashboard.system_health_endpoint import handle_system_health_request


class FakeQueue:
    def status(self):
        return {"health": "healthy", "counts": {"queued": 1}, "total": 1}


def test_system_health_endpoint_returns_unified_snapshot(tmp_path):
    audit = NotificationQueueAudit(tmp_path / "audit.json")
    audit.record(actor="test", action="delivered", item_id="n1", success=True)

    status, payload = handle_system_health_request(FakeQueue(), audit, "/api/system-health", tmp_path)

    assert status == 200
    assert payload["queue"]["health"] == "healthy"
    assert payload["audit"]["total"] == 1
    assert payload["audit"]["failed"] == 0
    assert payload["ci"]["status"] == "missing"


def test_system_health_endpoint_rejects_unknown_path(tmp_path):
    audit = NotificationQueueAudit(tmp_path / "audit.json")
    status, payload = handle_system_health_request(FakeQueue(), audit, "/api/other", tmp_path)

    assert status == 404
    assert payload == {"error": "not found"}
