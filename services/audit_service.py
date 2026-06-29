"""
Audit logging service.

Every significant action in the system (login, statement creation,
updates, deletions) should be recorded by calling `log_action`.
"""

from flask import request
from flask_login import current_user

from extensions import db
from models import AuditLog


def log_action(action: str, description: str = "", user_id: int = None):
    """Persist an audit log entry.

    Args:
        action: short machine-readable code, e.g. 'LOGIN', 'CREATE_STATEMENT'.
        description: human-readable detail of what happened.
        user_id: overrides the acting user (defaults to current_user if logged in).
    """
    if user_id is None and getattr(current_user, "is_authenticated", False):
        user_id = current_user.id

    entry = AuditLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    db.session.commit()
    return entry
