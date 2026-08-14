from core.voice_runtime import VoiceRuntime

class FakeListener:
    def __init__(self, text): self.text=text
    def listen(self): return self.text

class FakePipeline:
    def __init__(self): self.commands=[]
    def assistant(self, command):
        self.commands.append(command); return f"OK: {command}"

def test_runtime_activates_and_preserves_command_case():
    pipeline=FakePipeline(); spoken=[]
    result=VoiceRuntime(FakeListener("Nova, Open My Project"), pipeline, speak=spoken.append).run_once()
    assert result.activated
    assert pipeline.commands == ["Open My Project"]
    assert spoken == ["OK: Open My Project"]

def test_runtime_ignores_non_wake_word():
    pipeline=FakePipeline(); result=VoiceRuntime(FakeListener("hello assistant"), pipeline).run_once()
    assert not result.activated
    assert pipeline.commands == []
