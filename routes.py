from flask import Blueprint, request, jsonify, render_template, request, g, redirect, url_for, flash, session, send_file, make_response, current_app
from firebase_admin import auth, firestore
from services.middleware import firebase_required  
from services.firebase_config import db
from services.models import (
    create_user, get_user,
    create_activity, get_user_activities,
    create_certificate, get_user_certificates,
    create_recommendation, get_user_recommendations,
    create_verification, get_user_verifications,
    get_certificate, update_certificate, delete_certificate, 
    create_event, get_all_events,
    get_event, update_event, delete_event

)
from forms import RegistrationForm, LoginForm, CertificateForm, ActivityForm, UpdateProfileForm, AddRecommendationForm, EditRecommendationForm, NewsletterEventForm
from datetime import datetime, date
from utils import generate_csv_report, generate_pdf_report
from recommendation_engine import generate_recommendations
from verification_engine import verify_activities
from pdf_generator import generate_cpe_report
from werkzeug.utils import secure_filename
from uuid import uuid4
from google.cloud.firestore import FieldFilter
import os

routes_bp = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# ---------------------------
# Helper normalizers
# ---------------------------
def _normalize_cert(cert):
    """
    Ensure cert is a plain dict with expected keys and types.
    Accepts dict-like or Firestore doc dicts. Returns normalized dict.
    """
    if not isinstance(cert, dict):
        try:
            cert = dict(cert)
        except Exception:
            cert = {}

    # canonical keys and defaults
    cert_id = cert.get('id') or cert.get('cert_id') or cert.get('certificate_id') or ''
    cert.setdefault('id', cert_id)
    cert.setdefault('name', cert.get('name') or 'Unnamed Certification')
    cert.setdefault('authority', cert.get('authority') or '')
    cert.setdefault('required_cpes', cert.get('required_cpes') or 0)
    cert.setdefault('earned_cpes', cert.get('earned_cpes') or 0)
    cert.setdefault('progress_percentage', float(cert.get('progress_percentage') or 0.0))
    cert.setdefault('status', cert.get('status') or 'unknown')
    # Normalize renewal_date -> date object or None
    rd = cert.get('renewal_date')
    if isinstance(rd, date):
        cert['renewal_date'] = rd
    elif isinstance(rd, datetime):
        cert['renewal_date'] = rd.date()
    elif isinstance(rd, str) and rd:
        # try common formats
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'):
            try:
                cert['renewal_date'] = datetime.strptime(rd, fmt).date()
                break
            except Exception:
                cert['renewal_date'] = None
        # fallback to isoformat parse
        if cert.get('renewal_date') is None:
            try:
                cert['renewal_date'] = datetime.fromisoformat(rd).date()
            except Exception:
                cert['renewal_date'] = None
    else:
        cert['renewal_date'] = None

    # ensure numeric types
    try:
        cert['required_cpes'] = int(cert['required_cpes'])
    except Exception:
        cert['required_cpes'] = 0
    try:
        cert['earned_cpes'] = float(cert['earned_cpes'])
    except Exception:
        cert['earned_cpes'] = 0.0
    try:
        cert['progress_percentage'] = float(cert['progress_percentage'])
    except Exception:
        cert['progress_percentage'] = 0.0

    # activities subkey default
    cert.setdefault('activities', [])
    return cert

def _normalize_activity(act):
    """
    Ensure activity is a plain dict with expected keys and types.
    Returns normalized dict.
    """
    if not isinstance(act, dict):
        try:
            act = dict(act)
        except Exception:
            act = {}

    act.setdefault('title', act.get('title') or act.get('name') or '')
    act.setdefault('description', act.get('description') or act.get('desc') or '')

    # unify CPE field name to 'cpe_points'
    if 'cpe_points' not in act and 'cpe_value' in act:
        act['cpe_points'] = float(act.get('cpe_value') or 0)
    else:
        try:
            act['cpe_points'] = float(act.get('cpe_points') or 0)
        except Exception:
            act['cpe_points'] = 0.0

    # unify activity_date -> datetime/date
    date_obj = None
    for key in ('date', 'activity_date', 'activityDate', 'created_at'):
        if key in act and act[key]:
            val = act[key]
            try:
                # handle datetime or date objects
                if isinstance(val, (datetime, date)):
                    date_obj = val if isinstance(val, datetime) else datetime.combine(val, datetime.min.time())
                else:
                    date_obj = datetime.fromisoformat(str(val))
            except Exception:
                try:
                    date_obj = datetime.strptime(str(val), '%Y-%m-%d')
                except Exception:
                    date_obj = None
            break
    act['date_obj'] = date_obj
    act['formatted_date'] = date_obj.strftime('%B %d, %Y') if date_obj else (act.get('activity_date') or '')

    # keep certification id
    act['certification_id'] = act.get('certification_id') or act.get('cert_id') or act.get('certification') or ''

    # proof file normalization
    proof_file_name = act.get('proof_file') or ''
    act['proof_file'] = proof_file_name

    # generate proof file URL for templates
    if proof_file_name:
        try:
            from flask import url_for
            act['proof_file_url'] = url_for('static', filename=f'uploads/{proof_file_name}')
        except RuntimeError:
            # outside request context
            act['proof_file_url'] = f'/static/uploads/{proof_file_name}'
    else:
        act['proof_file_url'] = ''

    return act

# =====================
# Public Pages
# =====================
@routes_bp.route('/', methods=['GET'], endpoint='index')
def index():
    return render_template('index.html')

@routes_bp.route('/login', methods=['GET'], endpoint='login_page')
def login_page():
    form = LoginForm()
    return render_template('login.html', form=form)

@routes_bp.route('/register', methods=['GET', 'POST'], endpoint='register_page')
def register_page():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user_rec = auth.create_user(
                    email=form.email.data,
                    password=form.password.data
                )
                create_user(user_rec.uid, {
                    'name': form.name.data,
                    'email': form.email.data
                })
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('routes.login_page'))
            except Exception as e:
                flash(f'Error creating account: {str(e)}', 'danger')
        else:
            flash('Please fix the errors in the form.', 'danger')
    return render_template('register.html', form=form)

@routes_bp.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('routes.login_page'))

# =====================
# Dashboard
# =====================
@routes_bp.route('/dashboard', methods=['GET'], endpoint='dashboard_page')
@firebase_required
def dashboard_page():
    uid = g.uid
    certifications_raw = get_user_certificates(uid) or []
    all_activities_raw = get_user_activities(uid) or []

    # Normalize certificates
    certifications = []
    for cert in certifications_raw:
        c = _normalize_cert(cert)
        certifications.append(c)

    # Normalize activities
    activities = []
    for a in all_activities_raw:
        aa = _normalize_activity(a)
        # add certification authority by looking up the cert list
        cert_match = next((c for c in certifications if c.get('id') == aa.get('certification_id')), None)
        aa['certification_authority'] = cert_match['authority'] if cert_match else 'Unknown'
        activities.append(aa)

    # Sort activities by date (newest first) then take top 3
    activities_sorted = sorted(activities, key=lambda x: x['date_obj'] or datetime.min, reverse=True)
    recent_activities = activities_sorted[:3]

    # Build reminders
    reminders = []
    for cert in certifications:
        rd = cert.get('renewal_date')
        if rd:
            try:
                days_until_renewal = (rd - date.today()).days
            except Exception:
                days_until_renewal = None
            if days_until_renewal is not None and days_until_renewal <= 90 and cert.get('progress_percentage', 0.0) < 100:
                reminders.append({
                    'type': 'renewal',
                    'message': f"{cert['name']} renewal is in {days_until_renewal} days and you need {max(0, cert['required_cpes'] - cert['earned_cpes']):.1f} more CPEs",
                    'cert_id': cert['id'],
                    'cert_name': cert['name']
                })
        if cert.get('progress_percentage', 0.0) < 25:
            reminders.append({
                'type': 'low_progress',
                'message': f"{cert['name']} has very low progress ({cert['progress_percentage']:.1f}%)",
                'cert_id': cert['id'],
                'cert_name': cert['name']
            })

    return render_template(
        'dashboard.html',
        certifications=certifications,
        recent_activities=recent_activities,
        reminders=reminders,
        total_certifications=len(certifications),
        total_activities=len(all_activities_raw or [])
    )

# =====================
# Certificate Routes
# =====================
@routes_bp.route('/certificates', methods=['GET'], endpoint='list_certificates')
@firebase_required
def list_certificates():
    certs_raw = get_user_certificates(g.uid) or []
    certs = [_normalize_cert(c) for c in certs_raw]
    return render_template('certifications.html', certifications=certs)

@routes_bp.route('/certificates/new', methods=['GET', 'POST'], endpoint='add_certification')
@firebase_required
def add_certification():
    form = CertificateForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'name': form.name.data,
            'authority': form.authority.data,
            'required_cpes': form.required_cpes.data,
            'renewal_date': form.renewal_date.data.isoformat() if form.renewal_date.data else None
        }
        create_certificate(g.uid, data)
        flash('Certification added successfully!', 'success')
        return redirect(url_for('routes.list_certificates'))
    return render_template('add_certification.html', form=form, certification=None)

@routes_bp.route('/certificates/<cert_id>/recommendations', methods=['GET'], endpoint='get_recommendations')
@firebase_required
def get_recommendations(cert_id):
    uid = g.uid
    certs = get_user_certificates(uid) or []
    cert = next((c for c in certs if str(c.get('id')) == str(cert_id)), None)
    if not cert:
        return jsonify({'error': 'Certificate not found'}), 404

    try:
        recommendations = generate_recommendations(cert.get("name"), cert.get("authority"), uid)
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
      
@routes_bp.route('/certificates/<cert_id>/recommendations-page', methods=['GET'], endpoint='recommendations_page')
@firebase_required
def recommendations_page(cert_id):
    uid = g.uid
    certs_raw = get_user_certificates(uid) or []
    cert = next((c for c in certs_raw if str(c.get('id')) == str(cert_id)), None)
    if not cert:
        return render_template('404.html'), 404

    cert_norm = _normalize_cert(cert)

    try:
        rec_docs = (
            db.collection("recommendations")
              .where("approved", "==", True)
              .order_by("created_at", direction=firestore.Query.DESCENDING)
              .stream()
        )
        recommendations = []
        for doc in rec_docs:
            r = doc.to_dict()
            recommendations.append({
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "url": r.get("url", "#"),
                "type": r.get("type", ""),
                "provider": r.get("source") or r.get("provider") or "",
                "cpe": r.get("cpe", 0),
                "expires_at": r.get("expires_at").strftime("%B %d, %Y") if r.get("expires_at") else None
            })
    except Exception as e:
        print("Error fetching recommendations:", e)
        recommendations = []

    return render_template(
        "recommendations.html",
        certification=cert_norm,
        recommendations=recommendations
    )
 
@routes_bp.route('/certificates/<cert_id>/edit', methods=['GET', 'POST'])
@firebase_required
def edit_certification(cert_id):
    cert_raw = get_certificate(cert_id)
    if not cert_raw:
        flash('Certification not found.', 'error')
        return redirect(url_for('routes.list_certificates'))

    cert = _normalize_cert(cert_raw)
    if request.method == 'POST':
        updated_data = {
            'name': request.form.get('name'),
            'authority': request.form.get('authority'),
            'required_cpes': int(request.form.get('required_cpes') or 0),
            'renewal_date': request.form.get('renewal_date')
        }
        update_certificate(cert_id, updated_data)
        flash('Certification updated successfully.', 'success')
        return redirect(url_for('routes.list_certificates'))

    return render_template('edit_certificate.html', certification=cert)

@routes_bp.route('/certificates/<cert_id>/delete', methods=['POST'])
@firebase_required
def delete_certification(cert_id):
    user_id = g.uid
    delete_certificate(user_id, cert_id)
    flash('Certification deleted successfully.', 'success')
    return redirect(url_for('routes.list_certificates'))

# =====================
# Activity Routes
# =====================
@routes_bp.route('/activities', methods=['GET'], endpoint='list_activities')
@firebase_required
def list_activities():
    raw_activities = get_user_activities(g.uid) or []
    processed = []
    for a in raw_activities:
        act = _normalize_activity(a)
        processed.append(act)
    # sort newest first
    processed = sorted(processed, key=lambda x: x['date_obj'] or datetime.min, reverse=True)
    return render_template('activities.html', activities=processed)

@routes_bp.route('/activities/new', methods=['GET', 'POST'], endpoint='add_activity')
@firebase_required
def add_activity():
    uid = g.uid
    form = ActivityForm()

    # Populate certification choices dynamically
    certifications = get_user_certificates(uid) or []
    form.certification_id.choices = [
        (str(c.get('id') or ''), c.get('name') or 'Unnamed')
        for c in certifications
    ]

    # -------------------------------
    # Prefill form from URL params
    # -------------------------------
    if request.method == 'GET' and request.args:
        pre_title = request.args.get('prefill_title')
        pre_desc = request.args.get('prefill_description')
        pre_type = request.args.get('prefill_type')
        pre_cpe = request.args.get('prefill_cpe')
        pre_provider = request.args.get('prefill_provider')
        pre_cert = request.args.get('prefill_cert')

        if pre_title:
            form.title.data = pre_title
        if pre_desc:
            form.description.data = pre_desc
        if pre_type:
            form.activity_type.data = pre_type
        if pre_provider:
            form.provider.data = pre_provider
        if pre_cpe:
            try:
                form.cpe_points.data = int(float(pre_cpe))
            except Exception:
                form.cpe_points.data = None
        if pre_cert:
            form.certification_id.data = str(pre_cert)

    # -------------------------------
    # Handle form submit
    # -------------------------------
    if request.method == 'POST' and form.validate_on_submit():
        proof_file_name = None
        if form.proof_file.data:
            uploaded_file = form.proof_file.data
            filename = secure_filename(uploaded_file.filename)
            filename = f"{uuid4().hex}_{filename}"
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            file_path = os.path.join(uploads_dir, filename)
            uploaded_file.save(file_path)
            proof_file_name = filename

        activity_data = {
            'title': form.title.data,
            'provider': form.provider.data,
            'cpe_points': float(form.cpe_points.data or 0),
            'activity_type': form.activity_type.data,
            'description': form.description.data,
            'activity_date': form.activity_date.data.isoformat() if form.activity_date.data else None,
            'certification_id': form.certification_id.data,
            'proof_file': proof_file_name,
            'user_id': uid
        }

        create_activity(uid, activity_data)
        flash('Activity added successfully!', 'success')
        return redirect(url_for('routes.list_activities'))

    return render_template('add_activity.html', form=form)

@routes_bp.route('/activities/<activity_id>/edit', methods=['GET', 'POST'], endpoint='edit_activity')
@firebase_required
def edit_activity(activity_id):
    uid = g.uid

    # Fetch all activities and find the one with this ID
    raw_activities = get_user_activities(uid) or []
    activity = next((a for a in raw_activities if str(a.get('id')) == str(activity_id)), None)
    if not activity:
        flash('Activity not found.', 'danger')
        return redirect(url_for('routes.list_activities'))

    activity = _normalize_activity(activity)
    form = ActivityForm()

    # Populate certification choices dynamically
    certifications = get_user_certificates(uid) or []
    form.certification_id.choices = [
        (str(c.get('id') or c.get('cert_id') or ''), c.get('name') or 'Unnamed')
        for c in certifications
    ]

    if request.method == 'GET':
        # Prefill form with existing data
        form.title.data = activity.get('title')
        form.provider.data = activity.get('provider')
        form.cpe_points.data = activity.get('cpe_points')
        form.activity_type.data = activity.get('activity_type')
        form.description.data = activity.get('description')
        if activity.get('date_obj'):
            form.activity_date.data = activity['date_obj'].date()
        form.certification_id.data = activity.get('certification_id')

    if request.method == 'POST' and form.validate_on_submit():
        proof_file_name = activity.get('proof_file')  # keep old proof file if not changed
        if form.proof_file.data:
            uploaded_file = form.proof_file.data
            filename = secure_filename(uploaded_file.filename)
            filename = f"{uuid4().hex}_{filename}"
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            file_path = os.path.join(uploads_dir, filename)
            uploaded_file.save(file_path)
            proof_file_name = filename

        updated_data = {
            'title': form.title.data,
            'provider': form.provider.data,
            'cpe_points': float(form.cpe_points.data or 0),
            'activity_type': form.activity_type.data,
            'description': form.description.data,
            'activity_date': form.activity_date.data.isoformat() if form.activity_date.data else None,
            'certification_id': form.certification_id.data,
            'proof_file': proof_file_name
        }

        # We’ll need an update function in models.py — but for now use create_activity with same ID if your storage supports overwrite
        from services.models import update_activity
        update_activity(uid, activity_id, updated_data)

        flash('Activity updated successfully!', 'success')
        return redirect(url_for('routes.list_activities'))

    return render_template('edit_activity.html', form=form, activity=activity)

@routes_bp.route('/activities/<activity_id>/delete', methods=['POST'])
@firebase_required
def delete_activity(activity_id):
    from services.models import delete_activity as delete_activity_model
    try:
        delete_activity_model(g.uid, activity_id)
        flash('Activity deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting activity: {str(e)}', 'danger')
    return redirect(url_for('routes.list_activities'))

# =====================
# Recommendations Routes
# =====================

@routes_bp.route("/recommendations/add", methods=["GET", "POST"])
@firebase_required
def add_recommendation():
    form = AddRecommendationForm()
    if form.validate_on_submit():
        # Convert expires_at date to datetime if provided
        expires_at_dt = None
        if form.expires_at.data:
            expires_at_dt = datetime.combine(form.expires_at.data, datetime.min.time())

        data = {
            "title": form.title.data,
            "url": form.url.data,
            "type": form.type.data,
            "source": form.source.data,
            "description": form.description.data,
            "cpe": float(form.cpe.data) if form.cpe.data is not None else None,
            "expires_at": expires_at_dt,
            "created_at": datetime.utcnow(),
            "created_by_uid": g.uid,
            "created_by_email": g.user.get("email"),
            "approved": False
        }

        db.collection("recommendations").add(data)
        flash("Recommendation submitted for review!", "success")
        return redirect(url_for("routes.dashboard_page"))

    return render_template("add_recommendation.html", form=form)

@routes_bp.route("/recommendations/pending", methods=["GET"])
@firebase_required
def pending_recommendations():
    docs = db.collection("recommendations").where("approved", "==", False).stream()
    recs = [dict(doc.to_dict(), id=doc.id) for doc in docs]
    return render_template("pending_recommendations.html", recommendations=recs)

@routes_bp.route("/my-recommendations", methods=["GET"])
@firebase_required
def my_recommendations():
    uid = g.uid
    recs = db.collection("recommendations")\
        .where("created_by_uid", "==", uid)\
        .order_by("created_at", direction=firestore.Query.DESCENDING)\
        .stream()
    rec_list = [dict(doc.to_dict(), id=doc.id) for doc in recs]
    return render_template("my_recommendations.html", recommendations=rec_list)

@routes_bp.route("/edit-recommendation/<string:rec_id>", methods=["GET", "POST"])
@firebase_required
def edit_recommendation(rec_id):
    doc_ref = db.collection("recommendations").document(rec_id)
    doc = doc_ref.get()

    if not doc.exists:
        flash("Recommendation not found.", "danger")
        return redirect(url_for("routes.my_recommendations"))

    data = doc.to_dict()
    form = EditRecommendationForm()

    # Pre-populate form on GET
    if request.method == "GET":
        form.title.data = data.get("title")
        form.description.data = data.get("description")
        form.url.data = data.get("url")

        expires_at = data.get("expires_at")
        if expires_at:
            if isinstance(expires_at, datetime):
                form.expires_at.data = expires_at.date()
            else:  # If stored as string
                form.expires_at.data = datetime.strptime(expires_at, "%Y-%m-%d").date()

    if form.validate_on_submit():
        expires_at_datetime = datetime.combine(form.expires_at.data, datetime.min.time())
        doc_ref.update({
            "title": form.title.data,
            "description": form.description.data,
            "url": form.url.data,
            "expires_at": expires_at_datetime  # Corrected variable
        })
        flash("Recommendation updated successfully!", "success")
        return redirect(url_for("routes.my_recommendations"))

    return render_template("edit_recommendation.html", form=form)

@routes_bp.route("/recommendations/<rec_id>/delete-own", methods=["POST"])
@firebase_required
def delete_own_recommendation(rec_id):
    rec_ref = db.collection("recommendations").document(rec_id)
    rec = rec_ref.get()
    if rec.exists and rec.to_dict().get("created_by_uid") == g.uid:
        rec_ref.delete()
        flash("Recommendation deleted!", "success")
    return redirect(url_for("routes.my_recommendations"))


# =====================
# Export
# =====================
@routes_bp.route('/certificates/<cert_id>/export/<format>', methods=['GET'], endpoint='export_certification')
@firebase_required
def export_cert(cert_id, format):
    uid = g.uid
    certs = get_user_certificates(uid) or []
    cert = next((c for c in certs if (c.get('id') == cert_id or str(c.get('id')) == str(cert_id))), None)
    if not cert:
        return render_template('404.html'), 404

    activities = get_user_activities(uid) or []
    filtered = [a for a in activities if str(a.get("certification_id")) == str(cert_id)]

    if format == 'csv':
        csv_data = generate_csv_report(cert, filtered)
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        safe_name = (cert.get("name") or "report").replace(" ", "_")
        response.headers['Content-Disposition'] = f'attachment; filename={safe_name}_report.csv'
        return response

    if format == 'pdf':
        safe_name = (cert.get("name") or "report").replace(" ", "_")
        filename = f"{safe_name}_report.pdf"

        pdf_buffer = generate_cpe_report(
            holder_name=g.user.get("full_name") or g.user.get("name") or g.user.get("email"),
            certification=cert.get("name"),
            member_id=cert.get("id"),
            activity=filtered
        )

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    flash('Invalid export format.', 'danger')
    return redirect(url_for('routes.list_certificates'))


@routes_bp.route('/activities/<activity_id>/export/<format>', methods=['GET'], endpoint='export_activity')
@firebase_required
def export_activity(activity_id, format):
    uid = g.uid
    activities = get_user_activities(uid) or []
    activity = next((a for a in activities if str(a.get('id')) == str(activity_id)), None)
    if not activity:
        return render_template('404.html'), 404

    cert = next((c for c in get_user_certificates(uid) or [] if str(c.get('id')) == str(activity.get('certification_id'))), None)

    if format == 'pdf':
        safe_name = (activity.get("title") or "activity_report").replace(" ", "_")
        filename = f"{safe_name}.pdf"

        pdf_buffer = generate_cpe_report(
            holder_name=g.user.get("full_name") or g.user.get("name") or g.user.get("email"),
            certification=cert.get("name") if cert else "Unknown",
            member_id=cert.get("id") if cert else "N/A",
            activity=[activity]
        )

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    flash('Invalid export format for activity.', 'danger')
    return redirect(url_for('routes.list_activities'))


@routes_bp.route('/certificates/<cert_id>/export/select', methods=['GET', 'POST'], endpoint='select_activities_for_export')
@firebase_required
def select_activities_for_export(cert_id):
    uid = g.uid
    cert = next((c for c in get_user_certificates(uid) or [] if str(c.get('id')) == str(cert_id)), None)
    if not cert:
        return render_template('404.html'), 404

    activities = [a for a in get_user_activities(uid) or [] if str(a.get("certification_id")) == str(cert_id)]

    if request.method == 'POST':
        selected_ids = request.form.getlist('activity_ids')
        selected_activities = [a for a in activities if str(a.get('id')) in selected_ids]

        if not selected_activities:
            flash("Please select at least one activity.", "warning")
            return redirect(request.url)

        safe_name = (cert.get("name") or "report").replace(" ", "_")

        pdf_buffer = generate_cpe_report(
            holder_name=g.user.get("full_name") or g.user.get("name") or g.user.get("email"),
            certification=cert.get("name"),
            member_id=cert.get("id"),
            activity=selected_activities
        )

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={safe_name}_selected_activities.pdf'
        return response

    return render_template('select_activities.html', cert=cert, activities=activities)

# =====================
# Profile Page
# =====================
@routes_bp.route('/profile', methods=['GET', 'POST'], endpoint='profile_page')
@firebase_required
def profile_page():
    uid = g.uid
    user_ref = db.collection('users').document(uid)
    form = UpdateProfileForm()

    if form.validate_on_submit():
        update_data = {}

        # Full name update
        if form.full_name.data:
            update_data["full_name"] = form.full_name.data.strip()

        # Handle profile image upload
        if form.profile_image.data:
            file = form.profile_image.data
            if file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    # Ensure upload folder exists
                    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                    os.makedirs(upload_path, exist_ok=True)

                    # Unique filename (UID + timestamp)
                    new_filename = f"{uid}_{int(datetime.utcnow().timestamp())}.{ext}"
                    save_path = os.path.join(upload_path, new_filename)
                    file.save(save_path)

                    # Save relative URL for template rendering
                    update_data["profile_image"] = url_for(
                        'static', filename=f"uploads/{new_filename}"
                    )

        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            user_ref.update(update_data)
            flash("Profile updated successfully!", "success")
        else:
            flash("No changes made.", "info")
        return redirect(url_for('routes.profile_page'))

    # Get Firestore user data
    user_doc = user_ref.get()
    firestore_data = user_doc.to_dict() if user_doc.exists else {}

    # Get Firebase Auth user data
    try:
        auth_user = auth.get_user(uid)
        auth_data = {
            "email": auth_user.email,
            "email_verified": auth_user.email_verified,
            "photo_url": auth_user.photo_url
        }
    except Exception as e:
        auth_data = {"email": None, "email_verified": False, "photo_url": None}
        print("Error fetching Firebase Auth user:", e)

    # Merge
    user_data = {**firestore_data, **auth_data}

    # Format dates
    if "created_at" in firestore_data and firestore_data["created_at"]:
        try:
            user_data["created_at"] = firestore_data["created_at"].strftime("%Y-%m-%d")
        except AttributeError:
            pass
    if "updated_at" in firestore_data and firestore_data["updated_at"]:
        try:
            user_data["updated_at"] = firestore_data["updated_at"].strftime("%Y-%m-%d")
        except AttributeError:
            pass

    return render_template('profile.html', user_data=user_data, form=form)
# =====================
# Newsletter
# =====================
@routes_bp.route('/newsletter', methods=['GET'], endpoint='list_newsletter')
@firebase_required
def list_newsletter():
    """Show all events to everyone."""
    raw = get_all_events() or []
    events = []
    for e in raw:
        if isinstance(e.get('created_at'), datetime):
            e['created_at_display'] = e['created_at'].strftime('%Y-%m-%d')
        else:
            e['created_at_display'] = str(e.get('created_at') or '')

        if isinstance(e.get('date'), (datetime, date)):
            e['date_display'] = e['date'].strftime('%Y-%m-%d')
        else:
            e['date_display'] = str(e.get('date') or '')

        events.append(e)

    return render_template('newsletter.html', events=events)

@routes_bp.route('/my-newsletter', methods=['GET'], endpoint='my_newsletter')
@firebase_required
def my_newsletter():
    """
    Show events created by the logged-in user.
    NOTE: we avoid a Firestore where+order_by composite index by
    fetching events with get_all_events() and filtering in Python.
    """
    uid = g.uid

    # get_all_events already orders by created_at desc in models.py
    raw = get_all_events() or []

    # client-side filter (safe for moderate dataset sizes)
    events = [e for e in raw if e.get('created_by_uid') == uid]

    # normalize display fields (same style as list_newsletter)
    for e in events:
        created_at = e.get('created_at')
        if isinstance(created_at, datetime):
            e['created_at_display'] = created_at.strftime('%Y-%m-%d')
        else:
            e['created_at_display'] = str(created_at or '')

        ev_date = e.get('date')
        if isinstance(ev_date, (datetime, date)):
            e['date_display'] = ev_date.strftime('%Y-%m-%d')
        else:
            e['date_display'] = str(ev_date or '')

    return render_template('my_newsletter.html', events=events)

@routes_bp.route('/newsletter/add', methods=['GET', 'POST'], endpoint='add_newsletter')
@firebase_required
def add_newsletter():
    """Add a new event."""
    form = NewsletterEventForm()
    if form.validate_on_submit():
        event_date = None
        if form.date.data:
            event_date = datetime.combine(form.date.data, datetime.min.time())

        created_by_name = (
            g.user.get("full_name")
            or g.user.get("name")
            or g.user.get("email")
            or ""
        )

        data = {
            "title": form.title.data,
            "description": form.description.data,
            "date": event_date,
            "link": form.link.data or None,
            "created_at": datetime.utcnow(),
            "created_by_name": created_by_name
        }

        create_event(g.uid, data)  # uses generic event function
        flash('Event added successfully!', 'success')
        return redirect(url_for('routes.my_newsletter'))

    return render_template('add_newsletter.html', form=form)

@routes_bp.route('/newsletter/edit/<string:event_id>', methods=['GET', 'POST'], endpoint='edit_newsletter')
@firebase_required
def edit_newsletter(event_id):
    """Edit an existing event."""
    ev = get_event(event_id)
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('routes.my_newsletter'))

    if ev.get("created_by_uid") != g.uid:
        flash('You are not allowed to edit this event.', 'danger')
        return redirect(url_for('routes.my_newsletter'))

    form = NewsletterEventForm()

    if request.method == 'GET':
        form.title.data = ev.get('title')
        form.description.data = ev.get('description')
        if isinstance(ev.get('date'), datetime):
            form.date.data = ev['date'].date()
        form.link.data = ev.get('link')

    if form.validate_on_submit():
        event_date = None
        if form.date.data:
            event_date = datetime.combine(form.date.data, datetime.min.time())

        updated = {
            "title": form.title.data,
            "description": form.description.data,
            "date": event_date,
            "link": form.link.data or None
        }

        update_event(event_id, updated)
        flash('Event updated successfully!', 'success')
        return redirect(url_for('routes.my_newsletter'))

    return render_template('add_newsletter.html', form=form, event=ev)

@routes_bp.route('/newsletter/delete/<string:event_id>', methods=['POST'], endpoint='delete_newsletter')
@firebase_required
def delete_newsletter(event_id):
    """Delete an event."""
    ev = get_event(event_id)
    if not ev:
        flash('Event not found.', 'danger')
        return redirect(url_for('routes.my_newsletter'))

    if ev.get("created_by_uid") != g.uid:
        flash('You are not allowed to delete this event.', 'danger')
        return redirect(url_for('routes.my_newsletter'))

    delete_event(event_id)
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('routes.my_newsletter'))



