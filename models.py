"""
SQLAlchemy models for the Police Statement Management System.

Tables:
    User        - police officer / administrator accounts
    Case        - case records that statements are linked to
    Statement   - individual witness/victim/suspect/complainant statements
    AuditLog    - tracks creation, updates, deletions and login activity
"""

from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    rank = db.Column(db.String(64), nullable=True)
    officer_id = db.Column(db.String(32), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default="officer")  # 'officer' or 'admin'
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    statements = db.relationship("Statement", backref="officer", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", backref="user", lazy="dynamic")

    # Flask-Login expects `is_active`; map it to our own active flag.
    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------
class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    case_type = db.Column(db.String(64), nullable=False)
    date_reported = db.Column(db.Date, nullable=False, default=date.today)
    station_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    statements = db.relationship(
        "Statement", backref="case", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Case {self.case_number}>"


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------
class Statement(db.Model):
    __tablename__ = "statements"

    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Person giving the statement
    person_name = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    national_id = db.Column(db.String(64), nullable=True)
    occupation = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(32), nullable=True)

    # Statement details
    statement_type = db.Column(db.String(20), nullable=False)  # Witness/Victim/Suspect/Complainant
    statement_text = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    evidence_file = db.Column(db.String(255), nullable=True)  # uploaded file path
    photo_file = db.Column(db.String(255), nullable=True)  # uploaded photo path
    signature_data = db.Column(db.Text, nullable=True)  # base64 signature image

    statement_date = db.Column(db.Date, nullable=False, default=date.today)
    statement_time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Statement {self.statement_id}>"


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(64), nullable=False)  # e.g. CREATE_STATEMENT, LOGIN, DELETE_STATEMENT
    description = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id}>"
