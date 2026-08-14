from core.base_skill import BaseSkill

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Describe what this skill does"
    keywords = ["example phrase"]
    risk_level = "low"

    def handle(self, query: str, context=None) -> str:
        return "Skill response"
