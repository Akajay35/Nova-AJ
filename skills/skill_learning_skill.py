from core.base_skill import BaseSkill
from core.skill_learning_engine import SkillLearningEngine

class SkillLearningSkill(BaseSkill):
    name="skill_learning"; description="Propose and manage new skill capabilities"; keywords=["learn skill","skill proposal","pending skills","approve skill","reject skill"]
    def handle(self, query: str, context=None) -> str:
        engine=context.get("skill_learning") if context else SkillLearningEngine(); q=query.strip(); low=q.lower()
        if "pending skills" in low or "skill proposals" in low:
            items=engine.list_pending(); return "No pending skill proposals." if not items else "Pending: " + "; ".join(f"{x.name}: {x.description}" for x in items)
        if low.startswith("approve skill "):
            name=q[len("approve skill "):].strip(); return "Skill proposal approved for review." if engine.approve(name) else "Skill proposal not found."
        if low.startswith("reject skill "):
            name=q[len("reject skill "):].strip(); return "Skill proposal rejected." if engine.reject(name) else "Skill proposal not found."
        if low.startswith("learn skill "):
            name=q[len("learn skill "):].strip(); p=engine.propose(name, f"Capability for {name}", "Requested by the user"); return f"Proposed skill '{p.name}'. Approval is required before installation."
        return "I can propose, list, approve, or reject skills."
