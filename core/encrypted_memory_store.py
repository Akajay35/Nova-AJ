from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .memory_store import MemoryStore


class EncryptedMemoryStore(MemoryStore):
    """Local memory encrypted with authenticated AES-GCM.

    NOVA_MEMORY_KEY is supplied by the runtime environment and is never stored
    in the repository. Each write uses a fresh random nonce. Authentication
    failure causes the read to fail closed.
    """

    VERSION = "v1"
    NONCE_BYTES = 12

    def __init__(self, path: str = "data/memory.enc", secret: str | None = None):
        self._secret = secret or os.getenv("NOVA_MEMORY_KEY")
        if not self._secret:
            raise ValueError("NOVA_MEMORY_KEY is required for encrypted memory")
        super().__init__(path)

    def _key(self) -> bytes:
        return hashlib.sha256(self._secret.encode("utf-8")).digest()

    def _read(self):
        try:
            raw = base64.b64decode(self.path.read_text(encoding="utf-8"), validate=True)
            version, nonce, ciphertext = raw.split(b"|", 2)
            if version != self.VERSION.encode("ascii") or len(nonce) != self.NONCE_BYTES:
                return []
            data = AESGCM(self._key()).decrypt(nonce, ciphertext, version)
            items = json.loads(data.decode("utf-8"))
            return items if isinstance(items, list) else []
        except (OSError, ValueError, json.JSONDecodeError, TypeError, InvalidTag):
            return []

    def _write(self, items):
        payload = json.dumps(items[-self.MAX_MEMORIES:], ensure_ascii=False).encode("utf-8")
        nonce = os.urandom(self.NONCE_BYTES)
        version = self.VERSION.encode("ascii")
        ciphertext = AESGCM(self._key()).encrypt(nonce, payload, version)
        raw = version + b"|" + nonce + b"|" + ciphertext
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(base64.b64encode(raw).decode("ascii"), encoding="utf-8")


def migrate_plaintext_memory(
    source: str = "data/memory.json", target: str = "data/memory.enc", secret: str | None = None
) -> bool:
    """One-time migration helper; leaves the original file untouched."""
    if not Path(source).exists():
        return False
    try:
        data = json.loads(Path(source).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, list):
        return False
    store = EncryptedMemoryStore(target, secret)
    store._write(data)
    return True
