from __future__ import annotations
from typing import Callable, Any

class Microphone:
    """Provider-neutral microphone adapter. A capture callable can be injected by the platform."""
    def __init__(self, capture: Callable[[], Any] | None = None):
        self.capture = capture

    def listen(self):
        if self.capture is None:
            raise RuntimeError("No microphone capture provider configured")
        return self.capture()
