from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


class AssistantPort(Protocol):
    """Stable application boundary for desktop, Android, web, or voice clients."""

    def handle(self, query: str) -> str: ...

    def startup_diagnostics(self) -> dict[str, object]: ...


@dataclass(frozen=True)
class ClientCapabilities:
    """Describes what a future client can provide without changing core logic."""

    voice_input: bool = False
    voice_output: bool = False
    notifications: bool = False
    file_picker: bool = False
    background_tasks: bool = False


@dataclass(frozen=True)
class ClientAdapter:
    name: str
    capabilities: ClientCapabilities
    handle: Callable[[str], str]
