from __future__ import annotations

class SkillLearningLoop:
    """Turns an unhandled command into a reviewable skill proposal."""
    def __init__(self, matcher, learning_engine):
        self.matcher = matcher
        self.learning_engine = learning_engine

    def handle_capability_gap(self, command: str, suggested_name: str, description: str, reason: str):
        matches = self.matcher.match(command)
        if matches:
            return {"status": "skill_available", "matches": matches}
        proposal = self.learning_engine.propose(suggested_name, description, reason)
        return {"status": "proposal_created", "proposal": proposal}
