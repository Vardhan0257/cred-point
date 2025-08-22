from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, URLField, PasswordField, SubmitField, TextAreaField, DateField, DateTimeField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, NumberRange
from wtforms import SelectField, FileField
from wtforms.widgets import DateInput
from flask_wtf.file import FileField, FileAllowed

# =====================
# AUTH FORMS
# =====================
class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# =====================
# ACTIVITY FORM
# =====================
class ActivityForm(FlaskForm):
    # ...existing code...
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=200)])
    provider = StringField("Provider", validators=[DataRequired(), Length(min=2, max=100)])
    cpe_points = FloatField("CPE Points", validators=[DataRequired()])
    # Fields required by add_activity.html
    activity_type = SelectField("Activity Type", choices=[('course', 'Course'), ('conference', 'Conference'), ('webinar', 'Webinar'), ('self_study', 'Self-Study'), ('teaching', 'Teaching'), ('certification', 'Certification')], validators=[DataRequired()])
    certification_id = SelectField("Certification", choices=[], validators=[Optional()])
    description = TextAreaField("Description", validators=[DataRequired()])
    activity_date = DateField("Activity Date", format='%Y-%m-%d', validators=[DataRequired()],widget=DateInput())
    proof_file = FileField("Proof File", validators=[FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Allowed formats: PDF, PNG, JPG.')])  
    submit = SubmitField("Add Activity")

# =====================
# CERTIFICATE FORM
# =====================
class CertificateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=200)])
    authority = SelectField("Authority", choices=[
        ("ISC2", "ISC²"),
        ("EC-Council", "EC-Council"),
        ("CompTIA", "CompTIA"),
        ("OffSec", "OffSec")
    ], validators=[DataRequired()])
    required_cpes = IntegerField("Required CPEs", validators=[DataRequired()])
    renewal_date = DateField("Renewal Date", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Add Certificate")

# =====================
# RECOMMENDATION FORM
# =====================
class AddRecommendationForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    url = StringField("URL", validators=[DataRequired(), URL()])
    type = SelectField("Type", choices=[
        ("course", "Course"),
        ("webinar", "Webinar"),
        ("article", "Article"),
        ("event", "Event")
    ], validators=[DataRequired()])
    source = StringField("Source", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    cpe = DecimalField("CPE Points", validators=[DataRequired(), NumberRange(min=0)])
    expires_at = DateField("Expires At", validators=[DataRequired()], format="%Y-%m-%d")
    submit = SubmitField("Save Recommendation")    

class EditRecommendationForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    url = URLField("URL", validators=[URL(), Length(max=500)])
    expires_at = DateField("Expires At", validators=[DataRequired()], format="%Y-%m-%d")
    submit = SubmitField("Save Changes")

# =====================
# VERIFICATION FORM
# =====================
class VerificationForm(FlaskForm):
    activity_id = StringField("Activity ID", validators=[DataRequired()])
    status = StringField("Status", validators=[DataRequired()])
    submit = SubmitField("Add Verification")

# =====================
# PROFILE FORM
# =====================
class UpdateProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[Optional(), Length(max=100)])
    profile_image = FileField("Profile Image", validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Save Changes")

# =====================
# NEWSLETTER FORM
# =====================  
class NewsletterEventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    date = DateField("Event Date", validators=[Optional()])
    link = URLField("Event Link", validators=[Optional(), URL()])
    submit = SubmitField("Save Event")
