from ..models.audit_log import AuditLog

def log_action(db, user_id: int, username: str, action: str, details: str = None):
    log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        details=details
    )
    db.add(log)
    db.commit()