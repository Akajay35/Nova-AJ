from core.confirmation import ConfirmationManager

def test_confirmation_defaults_to_denied():
    result=ConfirmationManager().request("delete file", "files", "filesystem")
    assert not result.approved

def test_confirmation_uses_user_decision():
    manager=ConfirmationManager(lambda req: req.permission == "notifications")
    assert manager.request("notify", "reminders", "notifications").approved
    assert not manager.request("delete", "files", "filesystem").approved
