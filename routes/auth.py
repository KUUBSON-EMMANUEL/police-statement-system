"""
Authentication routes: login, logout, password change, and (admin-only)
officer account creation.
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User
from forms import LoginForm, ChangePasswordForm, CreateOfficerForm
from services.audit_service import log_action
from utils import admin_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()

        if user and user.is_active and user.check_password(form.password.data):
            session.permanent = True
            login_user(user)
            log_action("LOGIN", f"User '{user.username}' logged in.")
            flash(f"Welcome back, {user.full_name}.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        log_action("LOGIN_FAILED", f"Failed login attempt for username '{form.username.data}'.")
        flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("LOGOUT", f"User '{current_user.username}' logged out.")
    logout_user()
    flash("You have been logged out securely.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_action("PASSWORD_CHANGE", f"User '{current_user.username}' changed their password.")
            flash("Password updated successfully.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("change_password.html", form=form)


@auth_bp.route("/officers/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_officer():
    form = CreateOfficerForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("That username is already taken.", "danger")
        else:
            new_user = User(
                username=form.username.data.strip(),
                full_name=form.full_name.data.strip(),
                officer_id=form.officer_id.data.strip() or None,
                rank=form.rank.data.strip() or None,
                role=form.role.data,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            log_action("CREATE_USER", f"Admin '{current_user.username}' created account '{new_user.username}'.")
            flash(f"Officer account '{new_user.username}' created.", "success")
            return redirect(url_for("dashboard.officers"))
    return render_template("create_officer.html", form=form)
