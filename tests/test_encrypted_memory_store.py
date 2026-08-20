import base64
import json

import pytest

from core.encrypted_memory_store import EncryptedMemoryStore, migrate_plaintext_memory


def test_round_trip(tmp_path):
    path = tmp_path / "memory.enc"
    store = EncryptedMemoryStore(str(path), "test-secret")
    assert store.remember("name", "Ajay", "identity", approved=True)
    loaded = EncryptedMemoryStore(str(path), "test-secret")
    assert loaded.recall("name")[0].value == "Ajay"


def test_wrong_key_fails_closed(tmp_path):
    path = tmp_path / "memory.enc"
    store = EncryptedMemoryStore(str(path), "correct")
    store.remember("secret", "private", approved=True)
    wrong = EncryptedMemoryStore(str(path), "wrong")
    assert wrong.recall("secret") == []


def test_tampering_fails_closed(tmp_path):
    path = tmp_path / "memory.enc"
    store = EncryptedMemoryStore(str(path), "secret")
    store.remember("x", "value", approved=True)
    encoded = base64.b64decode(path.read_text())
    tampered = bytearray(encoded)
    tampered[-1] ^= 1
    path.write_text(base64.b64encode(tampered).decode())
    assert store.recall("x") == []


def test_plaintext_migration(tmp_path):
    source = tmp_path / "memory.json"
    target = tmp_path / "memory.enc"
    source.write_text(json.dumps([{"key": "city", "value": "Delhi", "category": "profile", "approved": True}]))
    assert migrate_plaintext_memory(str(source), str(target), "migration-key")
    store = EncryptedMemoryStore(str(target), "migration-key")
    assert store.recall("city")[0].value == "Delhi"


def test_missing_key_rejected(monkeypatch, tmp_path):
    monkeypatch.delenv("NOVA_MEMORY_KEY", raising=False)
    with pytest.raises(ValueError):
        EncryptedMemoryStore(str(tmp_path / "memory.enc"))
