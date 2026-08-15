from core.alert_delivery import AlertDelivery
from core.notification_queue import NotificationQueue


def test_duplicate_fingerprint_is_deduplicated_after_restart(tmp_path):
    path = tmp_path / "notifications.json"
    first = AlertDelivery(NotificationQueue(path))
    alert = {"title": "Test alert", "fingerprint": "same-event"}

    assert first.enqueue(alert) is not None

    second = AlertDelivery(NotificationQueue(path))
    assert second.enqueue(alert) is None


def test_different_fingerprints_are_queued(tmp_path):
    queue = NotificationQueue(tmp_path / "notifications.json")
    delivery = AlertDelivery(queue)

    assert delivery.enqueue({"title": "A", "fingerprint": "a"}) is not None
    assert delivery.enqueue({"title": "B", "fingerprint": "b"}) is not None
    assert len(queue.list()) == 2
