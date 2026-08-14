from core.base_skill import BaseSkill


class HelpSkill(BaseSkill):
    name = "help"
    keywords = ["what can you do", "help", "list your skills", "what are your skills"]

    def __init__(self, skill_manager=None):
        # skill_manager is injected by assistant.py after all skills load,
        # so this skill can report on the others.
        self.skill_manager = skill_manager

    def handle(self, query: str) -> str:
        if self.skill_manager:
            return self.skill_manager.list_skills()
        return "I can help with a few things, but I couldn't look up the full list right now."
