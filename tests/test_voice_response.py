from core.voice_response import VoiceResponseHandler

def test_reminder_is_spoken():
    spoken=[]
    handler=VoiceResponseHandler(spoken.append)
    response=handler.from_reminder({"text":"work on Nova"})
    assert response.text == "Reminder: work on Nova"
    assert spoken == ["Reminder: work on Nova"]
