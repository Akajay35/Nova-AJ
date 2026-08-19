from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC):
    name = "unnamed"
    description = ""
    keywords: list[str] = []
    risk_level = "low"
    required_permissions: tuple[str, ...] = ()

    @abstractmethod
    def handle(self, query: str, context: dict[str, Any] | None = None) -> str:
        raise NotImplementedError

    def matches(self, query: str) -> bool:
        text = query.lower().strip()
        return any(keyword.lower() in text for keyword in self.keywords)
