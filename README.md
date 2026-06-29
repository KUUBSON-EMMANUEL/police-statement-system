# Police Statement Management System (PSMS)

A secure Flask web application for recording, searching, editing, printing,
and exporting witness / victim / suspect / complainant statements.

## Features

- Officer login with hashed passwords (Werkzeug), CSRF protection, and a
  sliding 30-minute session timeout.
- Role-based access control: regular **officers** can record, search, view,
  and edit statements; only **administrators** can delete statements,
  register new officer accounts, and view the audit log.
- Dashboard with live counts (statements, cases, officers) and a recent
  activity table.
- Multi-section statement form: case info, person info, statement details,
  evidence/photo upload, and a canvas-based digital signature pad.
- Automatic statement numbering (`STM-2026-000001`, incrementing per year).
- Search by case number, person name, statement ID, officer name, statement
  type, or date range.
- Printable statement view (browser print) and a true PDF export
  (ReportLab), plus CSV export of search results.
- Full audit trail: every login, statement creation, update, deletion, and
  export is logged with timestamp, user, and IP address.
- Dark mode toggle, responsive layout with collapsible sidebar for mobile.

## Project Structure

```
PoliceStatementSystem/
├── app.py                 # Application factory + CLI commands
├── config.py              # Dev / production / testing configuration
├── extensions.py          # db, login_manager, csrf instances
├── models.py               # User, Case, Statement, AuditLog
├── forms.py                # WTForms (CSRF + validation)
├── utils.py                 # RBAC decorator, safe file upload helper
├── routes/
│   ├── auth.py             # login, logout, password change, officer creation
│   ├── dashboard.py        # stats dashboard, officer list
│   ├── statements.py       # add / view / edit / delete / print / PDF
│   ├── search.py           # search + CSV export
│   └── audit.py            # audit log (admin only)
├── services/
│   ├── audit_service.py    # log_action()
│   ├── id_generator.py     # generate_statement_id()
│   └── export_service.py   # PDF & CSV generation
├── templates/               # Jinja2 templates (Bootstrap 5)
├── static/css/style.css     # Sidebar layout, stat cards, dark mode
├── static/js/                # dark mode + sidebar toggle, signature pad
└── requirements.txt
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit SECRET_KEY for production use
export FLASK_CONFIG=development  # Windows: set FLASK_CONFIG=development
```

## Initialize the database and create the first administrator

```bash
flask --app app init-db
flask --app app seed-admin --username admin --password "ChangeMe@123"
```

(Running `python app.py` directly will also auto-create the tables and a
default `admin` / `Admin@12345` account on first run, for local convenience
only — always change this password immediately, and prefer the CLI command
above for anything beyond local testing.)

## Run

```bash
flask --app app run --debug
# or
python app.py
```

Visit `http://127.0.0.1:5000`.

## Switching to MySQL/PostgreSQL in production

Set the `DATABASE_URL` environment variable, e.g.:

```
DATABASE_URL=postgresql://user:password@host:5432/psms_db
```

and run `FLASK_CONFIG=production flask --app app init-db` to create the
schema in the new database.

## Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash`
  (PBKDF2-SHA256 by default) — never stored or logged in plain text.
- All forms use Flask-WTF, which provides CSRF tokens automatically.
- All database access goes through SQLAlchemy's ORM (parameterized
  queries), preventing SQL injection.
- Sessions are HttpOnly and SameSite=Lax, with a 30-minute sliding
  timeout; set `SESSION_COOKIE_SECURE = True` (already on in
  `ProductionConfig`) when serving over HTTPS.
- Only administrators can delete statements or view the audit log;
  enforced server-side via the `@admin_required` decorator, not just
  hidden in the UI.
- Uploaded files are renamed with a random UUID prefix and restricted to
  an allow-list of extensions to reduce path-traversal / executable-upload
  risk.

## Notes on the demo/default account

The seeded `admin` account and its default password are for local
development only. Change the password (via "Change Password" in the
sidebar) or delete the account and create a fresh one before any real
deployment.
