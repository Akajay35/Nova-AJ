from core.base_skill import BaseSkill
from core.skill_learning import SkillLearning

class SkillGrowthSkill(BaseSkill):
    name = "skill_growth"
    description = "Propose and inspect new assistant skills safely"
    keywords = ["new skill", "learn skill", "learn", "skill proposal", "missing skill"]

    def handle(self, query: str, context=None) -> str:
        learner = SkillLearning()
        text = query.strip()
        low = text.lower()
        if "list" in low or "show" in low:
            items = learner.list()
            if not items: return "There are no skill proposals yet."
            return "\n".join(f"#{x['id']} [{x['status']}] {x['request']}" for x in items[-10:])
        request = text
        for prefix in ["learn skill", "new skill", "learn", "skill proposal"]:
            if low.startswith(prefix):
                request = text[len(prefix):].lstrip(" :,-")
                break
        if not request: return "Tell me what capability you want Nova AJ to learn."
        proposal = learner.propose(request, "User-requested capability")
        return f"Skill proposal #{proposal['id']} created. It will require validation before activation."
