from __future__ import annotations

import hmac
import os


class NotificationQueueAuthorizer:
    """Optional shared-secret authorization for queue-management operations."""

    def __init__(self, token: str | None = None):
        self.token = token if token is not None else os.getenv("NOVA_AJ_QUEUE_TOKEN", "")

    def authorize(self, supplied_token: str | None) -> bool:
        if not self.token or not supplied_token:
            return False
        return hmac.compare_digest(self.token, supplied_token)

    def require(self, supplied_token: str | None) -> None:
        if not self.authorize(supplied_token):
            raise PermissionError("notification queue authorization required")
