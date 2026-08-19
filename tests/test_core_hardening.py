from pathlib import Path

from core.health_check import HealthCheck
from core.memory import MemoryStore


def test_memory_is_bounded_and_rejects_oversized_values(tmp_path: Path):
    store = MemoryStore(str(tmp_path / "memory.json"))
    item = store.remember("hello", "fact")
    assert item["text"] == "hello"
    assert store.search("hello")

    try:
        store.remember("x" * (store.MAX_TEXT_LENGTH + 1))
    except ValueError:
        pass
    else:
        raise AssertionError("oversized memory was accepted")


def test_empty_memory_search_is_safe(tmp_path: Path):
    store = MemoryStore(str(tmp_path / "memory.json"))
    assert store.search("") == []


def test_health_uses_component_health():
    class Component:
        def health(self):
            return {"available": False, "status": "offline"}

    result = HealthCheck({"component": Component()}).run()
    assert result["ok"] is False
    assert result["checks"]["component"]["status"] == "offline"
