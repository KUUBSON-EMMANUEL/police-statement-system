"""
WTForms definitions.

Using Flask-WTF forms gives us automatic CSRF protection plus
server-side input validation for every form in the system.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    TextAreaField,
    DateField,
    TimeField,
    SubmitField,
    HiddenField,
)
from wtforms.validators import DataRequired, Length, Optional, Regexp, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, message="Use at least 8 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Update Password")


class CreateOfficerForm(FlaskForm):
    """Admin-only form for registering new officer / admin accounts."""

    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    officer_id = StringField("Officer ID", validators=[Optional(), Length(max=32)])
    rank = StringField("Rank", validators=[Optional(), Length(max=64)])
    role = SelectField("Role", choices=[("officer", "Officer"), ("admin", "Administrator")])
    password = PasswordField("Temporary Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Create Account")


GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]

STATEMENT_TYPE_CHOICES = [
    ("Witness", "Witness"),
    ("Victim", "Victim"),
    ("Suspect", "Suspect"),
    ("Complainant", "Complainant"),
]

CASE_TYPE_CHOICES = [
    ("Theft", "Theft"),
    ("Assault", "Assault"),
    ("Robbery", "Robbery"),
    ("Burglary", "Burglary"),
    ("Fraud", "Fraud"),
    ("Homicide", "Homicide"),
    ("Domestic Violence", "Domestic Violence"),
    ("Traffic", "Traffic Accident"),
    ("Drug Offence", "Drug Offence"),
    ("Cybercrime", "Cybercrime"),
    ("Other", "Other"),
]


class StatementForm(FlaskForm):
    # --- Case information ---------------------------------------------------
    case_number = StringField(
        "Case Number",
        validators=[DataRequired(), Length(max=64)],
        description="If this case number already exists, the statement will be linked to it.",
    )
    case_type = SelectField("Case Type", choices=CASE_TYPE_CHOICES, validators=[DataRequired()])
    date_reported = DateField("Date Reported", validators=[DataRequired()])
    station_name = StringField("Station Name", validators=[DataRequired(), Length(max=120)])

    # --- Person giving statement ---------------------------------------------
    person_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[Optional()])
    dob = DateField("Date of Birth", validators=[Optional()])
    national_id = StringField("National ID Number", validators=[Optional(), Length(max=64)])
    occupation = StringField("Occupation", validators=[Optional(), Length(max=120)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Regexp(r"^[0-9+\-\s()]{6,20}$", message="Enter a valid phone number."),
        ],
    )

    # --- Statement details ---------------------------------------------------
    statement_date = DateField("Statement Date", validators=[DataRequired()])
    statement_time = TimeField("Statement Time", validators=[DataRequired()])
    statement_type = SelectField("Statement Type", choices=STATEMENT_TYPE_CHOICES, validators=[DataRequired()])
    statement_text = TextAreaField("Full Statement Text", validators=[DataRequired(), Length(min=10)])
    evidence = TextAreaField("Evidence Description", validators=[Optional()])
    notes = TextAreaField("Additional Notes", validators=[Optional()])

    evidence_file = FileField(
        "Evidence File",
        validators=[FileAllowed(["pdf", "doc", "docx", "png", "jpg", "jpeg"], "Unsupported file type.")],
    )
    photo_file = FileField(
        "Photo Attachment",
        validators=[FileAllowed(["png", "jpg", "jpeg"], "Photos must be PNG or JPG.")],
    )
    signature_data = HiddenField("Officer Signature")

    submit = SubmitField("Save Statement")


class SearchForm(FlaskForm):
    case_number = StringField("Case Number", validators=[Optional(), Length(max=64)])
    person_name = StringField("Person Name", validators=[Optional(), Length(max=120)])
    statement_id = StringField("Statement ID", validators=[Optional(), Length(max=32)])
    officer_name = StringField("Officer Name", validators=[Optional(), Length(max=120)])
    date_from = DateField("Date From", validators=[Optional()])
    date_to = DateField("Date To", validators=[Optional()])
    statement_type = SelectField(
        "Statement Type",
        choices=[("", "All")] + STATEMENT_TYPE_CHOICES,
        validators=[Optional()],
    )
    submit = SubmitField("Search")
