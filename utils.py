"""
Shared utility helpers: role-based access control decorators and
safe file-upload helpers.
"""

import os
import uuid
from functools import wraps

from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def admin_required(view_func):
    """Restrict a view to users with the 'admin' role (e.g. statement deletion)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage):
    """Safely persist an uploaded file under the configured upload folder.

    Returns the relative path (under static/) to store in the database,
    or None if no valid file was supplied.
    """
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    original_name = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, unique_name))
    return f"uploads/{unique_name}"
