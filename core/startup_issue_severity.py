from __future__ import annotations


class StartupIssueSeverity:
    """Classify startup diagnostic issues by operational impact."""

    HIGH = ("failed", "failure", "error", "exception", "cannot", "missing", "broken")
    MEDIUM = ("warning", "warn", "degraded", "slow", "unavailable")
    LOW = ("notice", "optional", "recommend", "info")

    @classmethod
    def classify(cls, issue: object) -> str:
        text = str(issue).lower()
        if any(word in text for word in cls.HIGH):
            return "high"
        if any(word in text for word in cls.MEDIUM):
            return "medium"
        if any(word in text for word in cls.LOW):
            return "low"
        return "medium"

    @classmethod
    def critical(cls, issue: object) -> bool:
        text = str(issue).lower()
        return any(word in text for word in ("critical", "fatal", "security"))

    @classmethod
    def label(cls, issue: object) -> str:
        return "critical" if cls.critical(issue) else cls.classify(issue)
