"""
Dashboard routes: overview statistics, recent statements, registered officers.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user

from extensions import db
from models import Statement, Case, User, AuditLog
from utils import admin_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    total_statements = Statement.query.count()
    total_cases = Case.query.count()
    total_officers = User.query.filter_by(role="officer").count() + User.query.filter_by(role="admin").count()
    recent_statements = (
        Statement.query.order_by(Statement.created_at.desc()).limit(8).all()
    )

    type_counts = {
        "Witness": Statement.query.filter_by(statement_type="Witness").count(),
        "Victim": Statement.query.filter_by(statement_type="Victim").count(),
        "Suspect": Statement.query.filter_by(statement_type="Suspect").count(),
        "Complainant": Statement.query.filter_by(statement_type="Complainant").count(),
    }

    return render_template(
        "dashboard.html",
        total_statements=total_statements,
        total_cases=total_cases,
        total_officers=total_officers,
        recent_statements=recent_statements,
        type_counts=type_counts,
    )


@dashboard_bp.route("/officers")
@login_required
@admin_required
def officers():
    all_officers = User.query.order_by(User.created_at.desc()).all()
    return render_template("officers.html", officers=all_officers)


@dashboard_bp.route("/system/reset", methods=["GET", "POST"])
@login_required
@admin_required
def reset_system():
    """Wipe ALL statements, cases, officers, and audit logs.

    This is intentionally a two-step process: GET shows a confirmation
    page, POST (with the typed confirmation phrase) performs the wipe.
    The current admin's own session is logged out afterward since their
    account no longer exists.
    """
    if request.method == "POST":
        if request.form.get("confirm_text") != "RESET":
            flash("You must type RESET exactly to confirm. Nothing was deleted.", "warning")
            return redirect(url_for("dashboard.reset_system"))

        # Order matters: children before parents to satisfy foreign keys.
        AuditLog.query.delete()
        Statement.query.delete()
        Case.query.delete()
        User.query.delete()
        db.session.commit()

        logout_user()
        flash(
            "The system has been fully reset. All data was deleted. "
            "Use 'flask --app app seed-admin' to create a new administrator account.",
            "warning",
        )
        return redirect(url_for("auth.login"))

    return render_template("reset_system.html")
