from __future__ import annotations

SEVERITIES = ("critical", "high", "medium", "low")


def summarize(details: list[dict]) -> dict:
    counts = {severity: 0 for severity in SEVERITIES}
    for event in details:
        for issue in event.get("issues", []):
            severity = issue.get("severity", "medium")
            if severity in counts:
                counts[severity] += 1

    if counts["critical"]:
        health = "critical"
    elif counts["high"]:
        health = "degraded"
    elif counts["medium"]:
        health = "attention"
    elif counts["low"]:
        health = "good"
    else:
        health = "healthy"

    return {"health": health, "counts": counts, "total_issues": sum(counts.values())}
