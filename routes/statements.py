"""
Statement management routes: registration, viewing, editing, deletion,
printing, and PDF export.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    Response,
)
from flask_login import login_required, current_user

from extensions import db
from models import Statement, Case, User
from forms import StatementForm
from services.audit_service import log_action
from services.id_generator import generate_statement_id
from services.export_service import statement_to_pdf
from utils import admin_required, save_upload

statements_bp = Blueprint("statements", __name__)


def _get_or_create_case(form):
    case = Case.query.filter_by(case_number=form.case_number.data.strip()).first()
    if case is None:
        case = Case(
            case_number=form.case_number.data.strip(),
            case_type=form.case_type.data,
            date_reported=form.date_reported.data,
            station_name=form.station_name.data.strip(),
        )
        db.session.add(case)
    else:
        # Keep case-level info up to date but never silently overwrite case_number
        case.case_type = form.case_type.data
        case.date_reported = form.date_reported.data
        case.station_name = form.station_name.data.strip()
    return case


@statements_bp.route("/statements/new", methods=["GET", "POST"])
@login_required
def add_statement():
    form = StatementForm()
    if form.validate_on_submit():
        case = _get_or_create_case(form)
        db.session.flush()  # ensure case.id is available

        evidence_path = save_upload(form.evidence_file.data) if form.evidence_file.data else None
        photo_path = save_upload(form.photo_file.data) if form.photo_file.data else None

        statement = Statement(
            statement_id=generate_statement_id(),
            case=case,
            officer_id=current_user.id,
            person_name=form.person_name.data.strip(),
            gender=form.gender.data,
            dob=form.dob.data,
            national_id=form.national_id.data,
            occupation=form.occupation.data,
            address=form.address.data,
            phone=form.phone.data,
            statement_type=form.statement_type.data,
            statement_text=form.statement_text.data.strip(),
            evidence=form.evidence.data,
            notes=form.notes.data,
            evidence_file=evidence_path,
            photo_file=photo_path,
            signature_data=form.signature_data.data or None,
            statement_date=form.statement_date.data,
            statement_time=form.statement_time.data,
        )
        db.session.add(statement)
        db.session.commit()

        log_action(
            "CREATE_STATEMENT",
            f"Officer '{current_user.username}' recorded statement {statement.statement_id} "
            f"for case {case.case_number}.",
        )
        flash(f"Statement {statement.statement_id} saved successfully.", "success")
        return redirect(url_for("statements.view_statement", statement_id=statement.id))

    return render_template("add_statement.html", form=form, mode="add")


@statements_bp.route("/statements/<int:statement_id>")
@login_required
def view_statement(statement_id):
    statement = Statement.query.get_or_404(statement_id)
    return render_template("view_statement.html", statement=statement)


@statements_bp.route("/statements/<int:statement_id>/print")
@login_required
def print_statement(statement_id):
    statement = Statement.query.get_or_404(statement_id)
    return render_template("print_statement.html", statement=statement)


@statements_bp.route("/statements/<int:statement_id>/pdf")
@login_required
def download_pdf(statement_id):
    statement = Statement.query.get_or_404(statement_id)
    pdf_bytes = statement_to_pdf(statement, statement.case, statement.officer)
    log_action("EXPORT_PDF", f"Statement {statement.statement_id} exported to PDF by '{current_user.username}'.")
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={statement.statement_id}.pdf"
        },
    )


@statements_bp.route("/statements/<int:statement_id>/edit", methods=["GET", "POST"])
@login_required
def edit_statement(statement_id):
    statement = Statement.query.get_or_404(statement_id)
    case = statement.case

    form = StatementForm(obj=None)
    if request.method == "GET":
        form = StatementForm(data={
            "case_number": case.case_number,
            "case_type": case.case_type,
            "date_reported": case.date_reported,
            "station_name": case.station_name,
            "person_name": statement.person_name,
            "gender": statement.gender,
            "dob": statement.dob,
            "national_id": statement.national_id,
            "occupation": statement.occupation,
            "address": statement.address,
            "phone": statement.phone,
            "statement_date": statement.statement_date,
            "statement_time": statement.statement_time,
            "statement_type": statement.statement_type,
            "statement_text": statement.statement_text,
            "evidence": statement.evidence,
            "notes": statement.notes,
            "signature_data": statement.signature_data,
        })

    if form.validate_on_submit():
        # Case number cannot be changed once a statement is filed under it;
        # officers must create a new statement to relink to a different case.
        case.case_type = form.case_type.data
        case.date_reported = form.date_reported.data
        case.station_name = form.station_name.data.strip()

        statement.person_name = form.person_name.data.strip()
        statement.gender = form.gender.data
        statement.dob = form.dob.data
        statement.national_id = form.national_id.data
        statement.occupation = form.occupation.data
        statement.address = form.address.data
        statement.phone = form.phone.data
        statement.statement_type = form.statement_type.data
        statement.statement_text = form.statement_text.data.strip()
        statement.evidence = form.evidence.data
        statement.notes = form.notes.data
        statement.statement_date = form.statement_date.data
        statement.statement_time = form.statement_time.data
        if form.signature_data.data:
            statement.signature_data = form.signature_data.data

        if form.evidence_file.data:
            new_path = save_upload(form.evidence_file.data)
            if new_path:
                statement.evidence_file = new_path
        if form.photo_file.data:
            new_path = save_upload(form.photo_file.data)
            if new_path:
                statement.photo_file = new_path

        db.session.commit()
        log_action(
            "UPDATE_STATEMENT",
            f"Officer '{current_user.username}' updated statement {statement.statement_id}.",
        )
        flash(f"Statement {statement.statement_id} updated.", "success")
        return redirect(url_for("statements.view_statement", statement_id=statement.id))

    # Force case_number field to read-only display on edit (still pre-filled)
    form.case_number.render_kw = {"readonly": True}
    return render_template("edit_statement.html", form=form, statement=statement, mode="edit")


@statements_bp.route("/statements/<int:statement_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_statement(statement_id):
    statement = Statement.query.get_or_404(statement_id)
    statement_ref = statement.statement_id
    db.session.delete(statement)
    db.session.commit()
    log_action(
        "DELETE_STATEMENT",
        f"Administrator '{current_user.username}' deleted statement {statement_ref}.",
    )
    flash(f"Statement {statement_ref} has been deleted.", "warning")
    return redirect(url_for("search.search_statements"))
