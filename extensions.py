"""
Central place for Flask extension instances.

Keeping these separate from app.py avoids circular imports between
app.py, models.py and the route blueprints.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access the Police Statement Management System."
login_manager.login_message_category = "warning"
