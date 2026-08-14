from config import CONFIRM_EXTERNAL_ACTIONS

class PermissionGate:
    def requires_confirmation(self, risk_level: str) -> bool:
        return CONFIRM_EXTERNAL_ACTIONS and risk_level in {"medium", "high", "critical"}

    def confirm(self, action: str) -> bool:
        answer = input(f"Nova AJ needs confirmation for: {action}. Continue? [y/N] ").strip().lower()
        return answer in {"y", "yes"}
