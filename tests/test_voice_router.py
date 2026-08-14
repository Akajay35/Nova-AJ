from core.voice_router import VoiceRouter

def test_routes_natural_commands():
    r=VoiceRouter()
    assert r.route("Can you remind me tomorrow?").intent == "reminder"
    assert r.route("What should I work on in my Nova project?").intent == "project"
    assert r.route("What are my priorities today?").intent == "daily_plan"
    assert r.route("Tell me something interesting").intent == "general"
