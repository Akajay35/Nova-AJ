from core.orchestrator import NovaOrchestrator

def test_orchestrator_routes_to_injected_handler():
    nova = NovaOrchestrator(handlers={"reminder": lambda text: "reminder handled"})
    result = nova.handle("Nova, remind me about my project")
    assert result.route.intent == "reminder"
    assert result.handler == "reminder"
    assert result.response == "reminder handled"

def test_orchestrator_falls_back_to_general():
    nova = NovaOrchestrator(general_handler=lambda text: f"AI: {text}")
    result = nova.handle("Tell me something interesting")
    assert result.route.intent == "general"
    assert result.handler == "general"
    assert result.response.startswith("AI:")
