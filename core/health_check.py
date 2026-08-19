from __future__ import annotations


class HealthCheck:
    """Component-aware diagnostics; hardware/API failures are reported, not hidden."""

    def __init__(self, components: dict[str, object]):
        self.components = components

    @staticmethod
    def _check(component: object) -> dict[str, object]:
        if component is None:
            return {"ok": False, "status": "missing", "type": None}
        health = getattr(component, "health", None)
        if callable(health):
            try:
                result = health()
                if isinstance(result, dict):
                    available = result.get("available", result.get("ok", True))
                    return {"ok": bool(available), "type": type(component).__name__, **result}
            except Exception as exc:
                return {"ok": False, "status": "health_error", "error": type(exc).__name__, "type": type(component).__name__}
        return {"ok": True, "status": "loaded", "type": type(component).__name__}

    def run(self) -> dict[str, object]:
        checks = {name: self._check(component) for name, component in self.components.items()}
        required_failures = [name for name, item in checks.items() if not item.get("ok", False)]
        return {"ok": not required_failures, "checks": checks}

    def summary(self) -> str:
        result = self.run()
        failed = [name for name, item in result["checks"].items() if not item["ok"]]
        return "Nova health check passed." if not failed else "Nova health check needs attention: " + ", ".join(failed)
