from datetime import datetime
import csv
import io
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

