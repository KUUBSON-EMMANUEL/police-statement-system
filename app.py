"""
Police Statement Management System
------------------------------------
Application entry point. Uses the application-factory pattern so the
app can be configured differently for development, testing, and
production deployments.

Run locally with:
    flask --app app run --debug
or simply:
    python app.py
"""

import os
import click
from datetime import datetime, timedelta

from flask import Flask, render_template, session
from flask_login import current_user

from config import config_map
from extensions import db, login_manager, csrf
from models import User


def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    app.config.from_object(config_map[config_name])

    # --- Initialize extensions -------------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # --- Register blueprints ----------------------------------------------------
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.statements import statements_bp
    from routes.search import search_bp
    from routes.audit import audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(statements_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(audit_bp)

    # --- Session timeout (sliding expiration) ------------------------------------
    @app.before_request
    def refresh_session():
        session.permanent = True
        app.permanent_session_lifetime = app.config["PERMANENT_SESSION_LIFETIME"]

    # --- Template globals ---------------------------------------------------------
    @app.context_processor
    def inject_globals():
        return {"now": datetime.utcnow()}

    # --- Error handlers -------------------------------------------------------------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="You do not have permission to view this page."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="The page you requested could not be found."), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413, message="The uploaded file is too large."), 413

    # --- CLI commands ----------------------------------------------------------------
    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("reset-db")
    @click.option(
        "--yes", is_flag=True,
        help="Skip the confirmation prompt (required for non-interactive use).",
    )
    def reset_db(yes):
        """Wipe ALL data (statements, cases, officers, audit logs) and recreate empty tables.

        This is destructive and cannot be undone. Uploaded evidence/photo
        files on disk are NOT deleted automatically; clear static/uploads/
        by hand if you also want those removed.
        """
        if not yes:
            click.confirm(
                "This will permanently delete ALL statements, cases, officers, "
                "and audit logs. Continue?",
                abort=True,
            )
        db.drop_all()
        db.create_all()
        click.echo("Database reset complete — all tables recreated empty.")
        click.echo("Run 'flask --app app seed-admin' to create a new administrator account.")

    @app.cli.command("seed-admin")
    @click.option("--username", default="admin", help="Admin username")
    @click.option("--password", default="Admin@12345", help="Admin password")
    def seed_admin(username, password):
        """Create a default administrator account if one doesn't already exist."""
        if User.query.filter_by(username=username).first():
            click.echo(f"User '{username}' already exists.")
            return
        admin = User(
            username=username,
            full_name="System Administrator",
            rank="Administrator",
            officer_id="ADMIN-001",
            role="admin",
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrator account '{username}' created with the supplied password.")
        click.echo("IMPORTANT: change this password immediately after first login.")

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Seed a default administrator on first run only, for local dev convenience.
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                full_name="System Administrator",
                rank="Administrator",
                officer_id="ADMIN-001",
                role="admin",
            )
            admin.set_password("Admin@12345")
            db.session.add(admin)
            db.session.commit()
            print("Default administrator created -> username: admin / password: Admin@12345")
            print("CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN.")

    app.run(debug=True)
