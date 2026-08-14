from core.memory_context import MemoryContext

class Memory:
    def search(self, q): return ["memory one", "memory two"]
class Profile:
    def summary(self): return {"goal": "build Nova"}

def test_memory_context_is_bounded():
    ctx = MemoryContext(Memory(), Profile())
    result = ctx.build("Nova")
    assert result["profile"]["goal"] == "build Nova"
    assert len(result["memories"]) == 2
