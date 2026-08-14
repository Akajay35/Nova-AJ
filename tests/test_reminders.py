from core.reminders import ReminderStore
from datetime import datetime, timezone, timedelta

def test_reminder_lifecycle(tmp_path):
    store=ReminderStore(str(tmp_path/"reminders.json")); due=(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat(); r=store.add("test", due)
    assert store.due()[0]["id"] == r["id"]
    assert store.complete(r["id"])
    assert store.due() == []
