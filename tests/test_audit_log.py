from core.audit_log import AuditLog

def test_audit_log_records_and_reads_recent(tmp_path):
    log=AuditLog(str(tmp_path/"audit.json")); log.record("permission", "web", "fetch", "denied", "blocked")
    recent=log.recent(); assert len(recent) == 1; assert recent[0]["decision"] == "denied"
