from __future__ import annotations

from typing import Any

from .profile import ProfileStore


def profile_handlers(profile: ProfileStore | None = None) -> dict[str, Any]:
    """Return safe handlers for explicit profile/preference changes."""
    store = profile or ProfileStore()
    return {
        "set_preference": lambda key, value: _set_preference(store, key, value),
        "add_goal": lambda text: _add(store, "goals", text),
        "add_project": lambda text: _add(store, "projects", text),
        "add_note": lambda text: _add(store, "notes", text),
        "remove_profile_item": lambda term: store.remove(term),
    }


def _set_preference(store: ProfileStore, key: str, value: str) -> str:
    key, value = key.strip(), value.strip()
    if not key or not value:
        raise ValueError("Preference key and value cannot be empty")
    store.set_preference(key, value)
    return f"Saved preference: {key} = {value}"


def _add(store: ProfileStore, category: str, text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Profile item cannot be empty")
    store.add(category, text)
    return f"Saved {category[:-1]}: {text}"
