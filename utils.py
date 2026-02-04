from datetime import datetime, date, timedelta
import csv
import io
from flask import url_for
from firebase_admin import storage
from services.models import (
    get_user_activities,
    get_user_certificates,
    get_user_recommendations,
    get_user_verifications
)

# =====================
# DATE UTILITIES
# =====================
def format_date(date_obj):
    """Format datetime/date object to string (DD-MM-YYYY)."""
    if not date_obj:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%d-%m-%Y")


# =====================
# SECURITY UTILITIES
# =====================
def get_secure_file_url(path_or_url):
    """
    Generates a secure URL for file access.
    - If HTTP URL (Legacy): Returns as is.
    - If Cloud Path: Generates a time-limited Signed URL (1 hour).
    - If Local File: Returns static URL.
    """
    if not path_or_url:
        return ""
    
    # Legacy public URLs
    if path_or_url.startswith('http'):
        return path_or_url
        
    # Cloud Storage Path (e.g., proofs/uid/file.jpg)
    if '/' in path_or_url and not path_or_url.startswith('static'):
        try:
            bucket = storage.bucket()
            blob = bucket.blob(path_or_url)
            # Generate signed URL valid for 60 minutes
            return blob.generate_signed_url(expiration=timedelta(minutes=60))
        except Exception as e:
            print(f"Error generating signed URL: {e}") # Fallback logging
            return ""
            
    # Local Static File (Legacy/Dev)
    try:
        return url_for('static', filename=f'uploads/{path_or_url}')
    except RuntimeError:
        return ""

# =====================
# DATA NORMALIZERS
# =====================
def normalize_cert(cert):
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

def normalize_activity(act):
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
    
    # Secure URL generation
    act['proof_file_url'] = get_secure_file_url(proof_file_name)

    return act


# =====================
# CPE POINTS CALCULATION
# =====================
def calculate_total_cpe(uid):
    """Sum all CPE points for a user."""
    activities = get_user_activities(uid)
    total_points = 0
    for activity in activities:
        total_points += int(activity.get("cpe_points", 0))
    return total_points


# =====================
# CERTIFICATE CHECK
# =====================
def get_active_certificates(uid):
    """Return only non-expired certificates for a user."""
    certificates = get_user_certificates(uid)
    active_certs = []
    today = datetime.utcnow().date()
    for cert in certificates:
        expiry_str = cert.get("expiry_date")
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if expiry_date >= today:
                    active_certs.append(cert)
            except ValueError:
                pass
        else:
            active_certs.append(cert)
    return active_certs


# =====================
# RECOMMENDATIONS FETCH
# =====================
def get_user_learning_resources(uid):
    """Return all recommendations for a user."""
    return get_user_recommendations(uid)


# =====================
# VERIFICATION STATUS
# =====================
def get_pending_verifications(uid):
    """Return only verifications with 'pending' status."""
    verifs = get_user_verifications(uid)
    return [v for v in verifs if v.get("status") == "pending"]


# =====================
# CSV REPORT GENERATOR
# =====================
def generate_csv_report(certification, activities):
    """Generate CSV data for a certification and its activities."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Certification Name", certification.get("name")])
    writer.writerow(["Authority", certification.get("authority")])
    writer.writerow(["Required CPEs", certification.get("required_cpes")])
    writer.writerow(["Earned CPEs", certification.get("earned_cpes")])
    writer.writerow(["Renewal Date", certification.get("renewal_date")])
    writer.writerow([])

    writer.writerow(["Activity Type", "Description", "CPE Value", "Date", "Verified"])
    for act in activities:
        writer.writerow([
            act.get("activity_type"),
            act.get("description"),
            act.get("cpe_value"),
            act.get("activity_date"),
            "Yes" if act.get("verified") else "No"
        ])

    output.seek(0)
    return output.read()

def generate_pdf_report(certification, activities):
    """Placeholder PDF generator (replace with real logic or external engine)."""
    from reportlab.pdfgen import canvas
    import io

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Certification: {certification.get('name')}")
    p.drawString(100, 780, f"Authority: {certification.get('authority')}")
    p.drawString(100, 760, f"Required CPEs: {certification.get('required_cpes')}")
    p.drawString(100, 740, f"Earned CPEs: {certification.get('earned_cpes')}")
    p.drawString(100, 720, f"Renewal Date: {certification.get('renewal_date')}")

    y = 700
    for act in activities:
        y -= 20
        p.drawString(100, y, f"{act.get('activity_type')} | {act.get('description')} | {act.get('cpe_value')} CPE")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
