"""Nova AJ configuration with safe environment parsing."""
from __future__ import annotations

import os


def _int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def _bool_env(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


ASSISTANT_NAME = os.getenv("NOVA_NAME", "Nova AJ").strip() or "Nova AJ"
WAKE_WORD = os.getenv("NOVA_WAKE_WORD", "nova aj").strip().lower() or "nova aj"
LANGUAGE = os.getenv("NOVA_LANGUAGE", "en-IN").strip() or "en-IN"
TTS_RATE = _int_env("NOVA_TTS_RATE", 175, 80, 300)
VOICE_MAX_TURNS = _int_env("NOVA_VOICE_MAX_TURNS", 8, 1, 30)
MEMORY_FILE = os.getenv("NOVA_MEMORY_FILE", "data/memory.json").strip() or "data/memory.json"
PROPOSAL_DIR = os.getenv("NOVA_PROPOSAL_DIR", "proposals").strip() or "proposals"
AI_PROVIDER = os.getenv("NOVA_AI_PROVIDER", "openai").strip().lower() or "openai"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"
CONFIRM_EXTERNAL_ACTIONS = _bool_env("NOVA_CONFIRM_EXTERNAL", True)
MAX_MEMORY_ITEMS = _int_env("NOVA_MAX_MEMORY", 500, 1, 5000)
