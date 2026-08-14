"""
COPY THIS FILE to create a new skill.

Rename it to something like `my_new_skill.py`, edit the class below,
and it will be picked up automatically the next time the assistant starts.
No other file needs to change.
"""

from core.base_skill import BaseSkill


class TemplateSkill(BaseSkill):
    # Shown in "what can you do" listings
    name = "template_skill"

    # Words/phrases that trigger this skill. Keep them distinct from other skills.
    keywords = ["trigger phrase here"]

    def handle(self, query: str) -> str:
        # `query` is the full text the user said (after the wake word).
        # Return the string you want the assistant to speak back.
        return "This is a placeholder response. Replace me with real logic!"
