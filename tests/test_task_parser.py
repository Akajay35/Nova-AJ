from datetime import datetime
from core.task_parser import NaturalTaskParser

def test_parses_tomorrow():
    result=NaturalTaskParser().parse("remind me to work on Nova tomorrow", datetime(2026,8,14,10,0))
    assert result.title == "work on Nova"
    assert result.due_date == "2026-08-15"

def test_parses_daily_recurring_task():
    result=NaturalTaskParser().parse("remind me daily to study")
    assert result.recurring == "daily"
    assert "study" in result.title
