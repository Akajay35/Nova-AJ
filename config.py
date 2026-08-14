"""Nova AJ configuration."""
import os

ASSISTANT_NAME = os.getenv("NOVA_NAME", "Nova AJ")
WAKE_WORD = os.getenv("NOVA_WAKE_WORD", "nova aj").lower()
LANGUAGE = os.getenv("NOVA_LANGUAGE", "en-IN")
TTS_RATE = int(os.getenv("NOVA_TTS_RATE", "175"))
VOICE_MAX_TURNS = int(os.getenv("NOVA_VOICE_MAX_TURNS", "8"))
MEMORY_FILE = os.getenv("NOVA_MEMORY_FILE", "data/memory.json")
PROPOSAL_DIR = os.getenv("NOVA_PROPOSAL_DIR", "proposals")
AI_PROVIDER = os.getenv("NOVA_AI_PROVIDER", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

# Safe-by-default: external/destructive actions require confirmation.
CONFIRM_EXTERNAL_ACTIONS = os.getenv("NOVA_CONFIRM_EXTERNAL", "true").lower() == "true"
MAX_MEMORY_ITEMS = int(os.getenv("NOVA_MAX_MEMORY", "500"))
