from __future__ import annotations

from core.alert_notification_status import route_alert
from core.notification_queue import NotificationQueue


class AlertDelivery:
    """Queue routed alerts once per fingerprint for provider-neutral delivery."""

    def __init__(self, queue: NotificationQueue):
        self.queue = queue
        self._queued_fingerprints: set[str] = {
            str(item.get("fingerprint", ""))
            for item in queue.list()
            if item.get("fingerprint")
        }

    def enqueue(self, alert: dict) -> dict | None:
        routed = route_alert(alert)
        fingerprint = str(routed.get("fingerprint", ""))
        if fingerprint and fingerprint in self._queued_fingerprints:
            return None
        item = self.queue.enqueue(routed)
        if fingerprint:
            self._queued_fingerprints.add(fingerprint)
        return item

    def enqueue_all(self, alerts: list[dict]) -> list[dict]:
        return [item for alert in alerts if (item := self.enqueue(alert)) is not None]
