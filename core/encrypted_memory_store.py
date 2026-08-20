from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from .memory_store import Memory, MemoryStore


class EncryptedMemoryStore(MemoryStore):
    """Local memory encryption using a secret supplied by the environment.

    The secret is never stored in the repository. Existing plaintext memory is
    migrated only when NOVA_MEMORY_KEY is available and migration is explicitly
    requested by the caller.
    """

    def __init__(self, path: str = "data/memory.enc", secret: str | None = None):
        self._secret = secret or os.getenv("NOVA_MEMORY_KEY")
        if not self._secret:
            raise ValueError("NOVA_MEMORY_KEY is required for encrypted memory")
        super().__init__(path)

    def _key(self) -> bytes:
        return hashlib.sha256(self._secret.encode("utf-8")).digest()

    def _crypt(self, data: bytes) -> bytes:
        key = self._key()
        return bytes(value ^ key[index % len(key)] for index, value in enumerate(data))

    def _read(self):
        try:
            raw = base64.b64decode(self.path.read_text(encoding="utf-8"))
            data = json.loads(self._crypt(raw).decode("utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError, json.JSONDecodeError):
            return []

    def _write(self, items):
        payload = json.dumps(items[-self.MAX_MEMORIES:], ensure_ascii=False).encode("utf-8")
        encrypted = base64.b64encode(self._crypt(payload)).decode("ascii")
        self.path.write_text(encrypted, encoding="utf-8")


def migrate_plaintext_memory(source: str = "data/memory.json", target: str = "data/memory.enc", secret: str | None = None) -> bool:
    """One-time migration helper; leaves the original file untouched."""
    if not Path(source).exists():
        return False
    store = EncryptedMemoryStore(target, secret)
    try:
        data = json.loads(Path(source).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, list):
        return False
    store._write(data)
    return True
