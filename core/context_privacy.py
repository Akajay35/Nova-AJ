from __future__ import annotations

from typing import Any


class ContextPrivacy:
    """Allowlist context fields that are safe and useful for AI prompts."""

    PROFILE_FIELDS = {"name", "preferences", "goals", "projects", "notes"}
    ITEM_FIELDS = {"role", "text", "timestamp", "kind"}

    def sanitize(self, context: Any) -> dict[str, Any]:
        if not isinstance(context, dict):
            return {"profile": {}, "relevant_memories": [], "relevant_conversations": []}

        profile = context.get("profile", {})
        if not isinstance(profile, dict):
            profile = {}
        safe_profile = {k: v for k, v in profile.items() if k in self.PROFILE_FIELDS}

        return {
            "profile": safe_profile,
            "relevant_memories": self._items(context.get("relevant_memories", [])),
            "relevant_conversations": self._items(context.get("relevant_conversations", [])),
        }

    def _items(self, items: Any) -> list[dict[str, Any]]:
        if not isinstance(items, list):
            return []
        result: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            result.append({k: v for k, v in item.items() if k in self.ITEM_FIELDS})
        return result
