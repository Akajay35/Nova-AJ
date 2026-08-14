from datetime import datetime, timezone, timedelta
from core.reminders import ReminderStore
from core.reminder_scheduler import ReminderScheduler

def test_scheduler_callback_once(tmp_path):
    store=ReminderStore(str(tmp_path/"reminders.json")); store.add("hello", (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat())
    seen=[]; scheduler=ReminderScheduler(store, on_due=seen.append)
    scheduler.check_once(); scheduler.check_once()
    assert len(seen) == 1
    assert seen[0]["text"] == "hello"
