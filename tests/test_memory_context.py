from core.memory_context import MemoryContext

class Memory:
    def search(self, q): return [{"key":"project", "value":"Nova AJ"}]
class Profile:
    def summary(self): return {"goal": "build Nova"}

def test_memory_context_is_bounded():
    ctx = MemoryContext(Memory(), Profile())
    result = ctx.build("Nova")
    assert result["profile"]["goal"] == "build Nova"
    assert result["memories"][0]["value"] == "Nova AJ"
    assert "Nova AJ" in ctx.build_text("Nova")
