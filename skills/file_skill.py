from __future__ import annotations

from pathlib import Path

from core.base_skill import BaseSkill


class FileSkill(BaseSkill):
    name = "files"
    description = "Lists files and creates simple text notes inside the Nova AJ workspace."
    keywords = ["list files", "show files", "create note", "make a note", "save a note"]

    root = Path("data")

    def handle(self, query: str, context: dict) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        lower = query.lower().strip()
        if lower.startswith(("list files", "show files")):
            files = sorted(p.name for p in self.root.iterdir() if p.is_file())
            return "Files: " + (", ".join(files) if files else "none")

        prefixes = ("create note", "make a note", "save a note")
        for prefix in prefixes:
            if lower.startswith(prefix):
                text = query[len(prefix):].strip(" :")
                if not text:
                    return "Tell me what you want in the note."
                path = self.root / "notes.txt"
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(text.replace("\n", " ") + "\n")
                return "Saved the note."
        return "I can list workspace files or save a text note."
