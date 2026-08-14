from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

@dataclass
class ParsedTask:
    title: str
    due_date: str | None = None
    recurring: str | None = None

class NaturalTaskParser:
    """Lightweight deterministic parser for common voice task phrases."""
    def parse(self, text: str, now: datetime | None = None) -> ParsedTask:
        now = now or datetime.now()
        value = text.strip()
        recurring = None
        if re.search(r"\bevery\s+day\b|\bdaily\b", value, re.I):
            recurring = "daily"
        elif re.search(r"\bevery\s+monday\b", value, re.I):
            recurring = "weekly:monday"
        due = None
        if re.search(r"\btomorrow\b", value, re.I):
            due = (now + timedelta(days=1)).date().isoformat()
        elif re.search(r"\btoday\b", value, re.I):
            due = now.date().isoformat()
        title = re.sub(r"\b(remind me to|remind me|every\s+day|daily|every\s+monday|tomorrow|today)\b", "", value, flags=re.I).strip(" ,.")
        return ParsedTask(title=title or value, due_date=due, recurring=recurring)
