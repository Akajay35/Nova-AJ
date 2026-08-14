from __future__ import annotations

class HealthCheck:
    """Lightweight startup diagnostics for Nova's required components."""
    def __init__(self, components: dict[str, object]):
        self.components = components

    def run(self):
        checks = {}
        for name, component in self.components.items():
            checks[name] = {"ok": component is not None, "type": type(component).__name__ if component is not None else None}
        return {
            "ok": all(item["ok"] for item in checks.values()),
            "checks": checks,
        }

    def summary(self) -> str:
        result = self.run()
        failed = [name for name, item in result["checks"].items() if not item["ok"]]
        return "Nova health check passed." if not failed else "Nova health check failed: " + ", ".join(failed)
