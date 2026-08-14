from core.notification_bridge import NotificationBridge

def test_notification_bridge_calls_callback():
    received=[]
    bridge=NotificationBridge(received.append)
    assert bridge.notify("Reminder due") == "Reminder due"
    assert received == ["Reminder due"]
    assert bridge.last() == "Reminder due"
    bridge.clear()
    assert bridge.last() is None
