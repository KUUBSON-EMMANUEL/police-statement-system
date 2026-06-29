"""
Search routes: filter statements by case number, person name, statement ID,
date range, officer name, or statement type. Also supports CSV export of
the filtered result set.
"""

from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user

from models import Statement, Case, User
from forms import SearchForm
from services.export_service import statements_to_csv
from services.audit_service import log_action
from extensions import db

search_bp = Blueprint("search", __name__)


def _apply_filters(form):
    query = Statement.query.join(Case).join(User, Statement.officer_id == User.id)

    if form.case_number.data:
        query = query.filter(Case.case_number.ilike(f"%{form.case_number.data.strip()}%"))
    if form.person_name.data:
        query = query.filter(Statement.person_name.ilike(f"%{form.person_name.data.strip()}%"))
    if form.statement_id.data:
        query = query.filter(Statement.statement_id.ilike(f"%{form.statement_id.data.strip()}%"))
    if form.officer_name.data:
        query = query.filter(User.full_name.ilike(f"%{form.officer_name.data.strip()}%"))
    if form.statement_type.data:
        query = query.filter(Statement.statement_type == form.statement_type.data)
    if form.date_from.data:
        query = query.filter(Statement.statement_date >= form.date_from.data)
    if form.date_to.data:
        query = query.filter(Statement.statement_date <= form.date_to.data)

    return query.order_by(Statement.created_at.desc())


@search_bp.route("/statements/search", methods=["GET", "POST"])
@login_required
def search_statements():
    form = SearchForm(request.args, meta={"csrf": False})
    results = []
    searched = bool(request.args)

    if searched:
        results = _apply_filters(form).all()

    return render_template("search_statement.html", form=form, results=results, searched=searched)


@search_bp.route("/statements/export/csv")
@login_required
def export_csv():
    form = SearchForm(request.args, meta={"csrf": False})
    results = _apply_filters(form).all()
    csv_bytes = statements_to_csv(results)
    log_action("EXPORT_CSV", f"User '{current_user.username}' exported {len(results)} statement(s) to CSV.")
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=statements_export.csv"},
    )
