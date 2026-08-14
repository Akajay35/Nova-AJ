from datetime import datetime
from core.base_skill import BaseSkill

class TimeSkill(BaseSkill):
    name = "time"; description = "Current local date and time"; keywords = ["time", "date", "today", "day"]
    def handle(self, query: str, context=None) -> str:
        now = datetime.now(); return now.strftime("It is %I:%M %p on %A, %d %B %Y.")
