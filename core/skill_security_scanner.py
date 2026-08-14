from __future__ import annotations

class SkillSecurityScanner:
    """Conservative pre-install scanner for declarative skill manifests."""
    ALLOWED_PERMISSIONS = {"", "task_read", "task_write", "memory_read", "memory_write", "skill_execute", "notification"}

    def scan_manifest(self, manifest: dict):
        findings=[]
        permissions=manifest.get("permissions", [])
        if not isinstance(permissions, list):
            findings.append({"severity":"high", "code":"permissions_not_list"})
            return {"safe":False,"findings":findings}
        for permission in permissions:
            if permission not in self.ALLOWED_PERMISSIONS:
                findings.append({"severity":"high", "code":"unknown_permission", "permission":permission})
        if not isinstance(manifest.get("name"), str) or not manifest.get("name", "").strip():
            findings.append({"severity":"high", "code":"invalid_name"})
        if not isinstance(manifest.get("version"), str) or not manifest.get("version", "").strip():
            findings.append({"severity":"medium", "code":"invalid_version"})
        return {"safe":not any(f["severity"] == "high" for f in findings), "findings":findings}
