from core.notification_dispatcher import NotificationDispatcher

def test_dispatcher_sends_reminder_to_sink():
    sent=[]
    dispatcher=NotificationDispatcher(sent.append)
    notification=dispatcher.dispatch_reminder({"text":"Work on Nova"})
    assert sent == [notification]
    assert notification.title == "Nova reminder"
    assert notification.message == "Work on Nova"
