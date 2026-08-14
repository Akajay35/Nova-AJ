from datetime import datetime

from core.base_skill import BaseSkill


class TimeSkill(BaseSkill):
    name = "time_and_date"
    keywords = ["what time", "current time", "what's the date", "today's date", "what day"]

    def handle(self, query: str) -> str:
        now = datetime.now()
        if "date" in query.lower() or "day" in query.lower():
            return f"Today is {now.strftime('%A, %B %d, %Y')}."
        return f"It's {now.strftime('%I:%M %p')} right now."
