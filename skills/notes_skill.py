import os
from datetime import datetime

from core.base_skill import BaseSkill
import config


class NotesSkill(BaseSkill):
    name = "notes"
    keywords = ["take a note", "remember that", "note that", "read my notes", "what are my notes"]

    def __init__(self):
        os.makedirs(config.DATA_FOLDER, exist_ok=True)
        self.filepath = os.path.join(config.DATA_FOLDER, "notes.txt")

    def handle(self, query: str) -> str:
        lower = query.lower()

        if "read" in lower or "what are" in lower:
            return self._read_notes()

        # Strip the trigger phrase so only the actual note content is saved.
        for trigger in ["take a note", "remember that", "note that"]:
            if trigger in lower:
                content = query.lower().split(trigger, 1)[1].strip()
                break
        else:
            content = query

        if not content:
            return "What would you like me to note down?"

        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {content}\n")

        return "Got it, I've saved that note."

    def _read_notes(self) -> str:
        if not os.path.exists(self.filepath):
            return "You don't have any notes yet."

        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return "You don't have any notes yet."

        latest = lines[-5:]
        return "Here are your most recent notes: " + "; ".join(
            line.split("] ", 1)[-1].strip() for line in latest
        )
