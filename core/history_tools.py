from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .conversation_history import ConversationHistory


def history_handlers(history: ConversationHistory) -> dict[str, Any]:
    def search_history(term: str, days: int = 30) -> list[dict[str, Any]]:
        cleaned = term.strip().lower()
        if not cleaned:
            raise ValueError("History search term cannot be empty")
        try:
            window = max(1, min(int(days), 365))
        except (TypeError, ValueError):
            window = 30
        cutoff = datetime.now(timezone.utc) - timedelta(days=window)
        results = []
        for entry in history.recent(history.limit):
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"])
            except (KeyError, TypeError, ValueError):
                continue
            if timestamp < cutoff:
                continue
            if cleaned in str(entry.get("text", "")).lower():
                results.append(entry)
        return results

    def history_for_day(day: str = "today") -> list[dict[str, Any]]:
        normalized = day.strip().lower()
        now = datetime.now(timezone.utc)
        if normalized in {"today", "todays", "today's"}:
            target = now.date()
        elif normalized in {"yesterday", "yesterdays", "yesterday's"}:
            target = (now - timedelta(days=1)).date()
        else:
            try:
                target = datetime.strptime(normalized, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError("Use today, yesterday, or YYYY-MM-DD") from exc
        return [
            entry for entry in history.recent(history.limit)
            if str(entry.get("timestamp", ""))[:10] == target.isoformat()
        ]

    return {"search_history": search_history, "history_for_day": history_for_day}
