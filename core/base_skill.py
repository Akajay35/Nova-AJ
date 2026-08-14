"""
Every skill in the skills/ folder must define a class that inherits from BaseSkill.
This is the only contract the skill system relies on, so adding new abilities to
the assistant never requires touching core code.
"""

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    # Short, human-readable name shown in logs / "what can you do" listings.
    name = "unnamed_skill"

    # List of trigger words/phrases that suggest this skill should handle the query.
    keywords = []

    def can_handle(self, query: str) -> bool:
        """
        Return True if this skill should handle the given query.
        Default implementation checks for any keyword match; override for
        custom logic (regex, intent scoring, etc.).
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)

    @abstractmethod
    def handle(self, query: str) -> str:
        """
        Process the query and return the text the assistant should speak back.
        """
        raise NotImplementedError
