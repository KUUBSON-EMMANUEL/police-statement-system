"""
Audit log routes (administrator only): review login activity, statement
creation, updates, and deletions.
"""

from flask import Blueprint, render_template, request

from models import AuditLog, User
from utils import admin_required
from flask_login import login_required

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/audit-log")
@login_required
@admin_required
def audit_log():
    page = request.args.get("page", 1, type=int)
    pagination = (
        AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=25, error_out=False)
    )
    return render_template("audit_log.html", pagination=pagination, logs=pagination.items)
