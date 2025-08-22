from .firebase_config import db
from datetime import datetime, date
from firebase_admin import firestore 
from google.cloud.firestore import FieldFilter
from flask import g
# ========================

def _recalculate_certificate_earned_cpes(uid, cert_id):
    """Re-sums all activities for a certificate and updates the certificate doc."""
    if not cert_id:
        return
    cert_ref = db.collection('users').document(uid).collection('certificates').document(str(cert_id))
    cert_doc = cert_ref.get()
    if not cert_doc.exists:
        return

    acts = db.collection('users').document(uid).collection('activities') \
             .where('certification_id', '==', cert_id).stream()
    total_cpe = sum(float(a.to_dict().get('cpe_points') or 0) for a in acts)

    required = float(cert_doc.to_dict().get('required_cpes') or 0) or 1.0
    progress = round((total_cpe / required) * 100, 2) if required else 0.0

    try:
        cert_ref.update({
            'earned_cpes': total_cpe,
            'progress_percentage': progress
        })
    except Exception:
        # best-effort: try set if update fails for missing doc
        cert_ref.set({
            'earned_cpes': total_cpe,
            'progress_percentage': progress
        }, merge=True)

def _recalc_user_credits(uid):
    """Recompute total credits from all activities and write to user document."""
    acts = db.collection('users').document(uid).collection('activities').stream()
    total = sum(float(a.to_dict().get('cpe_points') or 0) for a in acts)
    try:
        db.collection('users').document(uid).update({'credits': total})
    except Exception:
        db.collection('users').document(uid).set({'credits': total}, merge=True)


# ========================
# USER COLLECTION
# ========================
def create_user(uid, data):
    data['created_at'] = datetime.utcnow()
    db.collection("users").document(uid).set(data)

def get_user(uid):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def update_user(uid, updates):
    updates['updated_at'] = datetime.utcnow()
    db.collection("users").document(uid).update(updates)


# ========================
# ACTIVITIES COLLECTION (per user)
# ========================
def create_activity(uid, data):
    """
    Create an activity doc, normalize fields, increment user credits and recalc cert totals.
    Returns the new activity id.
    """
    # normalize cpe_points
    try:
        cpe = float(data.get('cpe_points') or data.get('cpe_value') or 0)
    except Exception:
        cpe = 0.0
    data['cpe_points'] = cpe

    # timestamp
    data['created_at'] = datetime.utcnow()

    # create document with generated id
    ref = db.collection("users").document(uid).collection("activities").document()
    data_to_store = dict(data)
    # include id in document (helps your client-side lists that look for 'id')
    data_to_store.setdefault('id', ref.id)

    ref.set(data_to_store)

    # increment user's credits atomically; fallback to full recalculation if update fails
    user_ref = db.collection('users').document(uid)
    try:
        user_ref.update({'credits': firestore.Increment(cpe)})
    except Exception:
        # fallback to full recalc if something prevents increment
        _recalc_user_credits(uid)

    # if linked to a certificate, recalc that certificate totals
    cert_id = data.get('certification_id')
    if cert_id:
        _recalculate_certificate_earned_cpes(uid, cert_id)

    return ref.id

def get_user_activities(uid):
    docs = db.collection("users").document(uid).collection("activities").stream()
    activities = []
    for doc in docs:
        a = doc.to_dict()
        a['id'] = doc.id
        activities.append(a)
    return activities

def update_activity(uid, activity_id, data):
    """
    Update an activity doc, adjust user credits by delta, and recalc affected certificates.
    """
    activity_ref = db.collection("users").document(uid).collection("activities").document(str(activity_id))
    # fetch existing activity (if any)
    old_doc = activity_ref.get()
    if not old_doc.exists:
        raise ValueError(f"Activity {activity_id} not found for user {uid}")

    old = old_doc.to_dict() or {}
    try:
        old_cpe = float(old.get('cpe_points') or 0)
    except Exception:
        old_cpe = 0.0
    old_cert = old.get('certification_id')

    # normalize incoming cpe_points if present
    if 'cpe_points' in data:
        try:
            new_cpe = float(data.get('cpe_points') or 0)
        except Exception:
            new_cpe = old_cpe
        data['cpe_points'] = new_cpe
    else:
        new_cpe = old_cpe

    # add updated_at
    data['updated_at'] = datetime.utcnow()

    # perform update
    activity_ref.update(data)

    # update user's credits by the delta (atomic increment when possible)
    delta = new_cpe - old_cpe
    if delta != 0:
        try:
            db.collection('users').document(uid).update({'credits': firestore.Increment(delta)})
        except Exception:
            _recalc_user_credits(uid)

    # recalc any affected certificates (old and new)
    new_cert = data.get('certification_id') or old_cert
    affected = set(filter(None, (old_cert, new_cert)))
    for cert_id in affected:
        _recalculate_certificate_earned_cpes(uid, cert_id)

    # keep API parity (no explicit return)
    return

def delete_activity(uid, activity_id):
    user_ref = db.collection("users").document(uid)
    activity_ref = user_ref.collection("activities").document(activity_id)
    
    # Get the activity before deletion
    activity_doc = activity_ref.get()
    if activity_doc.exists:
        activity_data = activity_doc.to_dict()
        cpe_points = float(activity_data.get("cpe_points", 0))  # Consistent key
        cert_id = activity_data.get("certification_id")

        # Delete activity
        activity_ref.delete()

        # Recalculate credits for the specific certificate
        if cert_id:
            _recalculate_certificate_earned_cpes(uid, cert_id)

        # Recalculate overall user credits
        _recalc_user_credits(uid)

    else:
        # No activity found, just exit
        return


# ========================
# CERTIFICATES COLLECTION (per user)
# ========================
def create_certificate(uid, data):
    data['created_at'] = datetime.utcnow()
    ref = db.collection("users").document(uid).collection("certificates").document()
    ref.set(data)
    return ref.id

def get_user_certificates(uid):
    docs = db.collection("users").document(uid).collection("certificates").stream()
    certs = []
    today = date.today()

    for doc in docs:
        cert = doc.to_dict()
        earned = cert.get('earned_cpes', 0)
        required = cert.get('required_cpes', 1)
        progress = round((earned / required) * 100, 2) if required > 0 else 0

        cert['earned_cpes'] = earned
        cert['required_cpes'] = required
        cert['progress_percentage'] = progress

        # Renewal date handling
        renewal_date = cert.get('renewal_date')
        days_left = None
        if renewal_date:
            if isinstance(renewal_date, datetime):
                renewal_date = renewal_date.date()
            elif isinstance(renewal_date, str):
                try:
                    renewal_date = datetime.strptime(renewal_date, "%Y-%m-%d").date()
                except ValueError:
                    renewal_date = None  # skip if format is bad

            if isinstance(renewal_date, date):
                days_left = (renewal_date - today).days

        # Status
        if progress >= 100:
            cert['status'] = 'complete'
        elif days_left is not None and days_left <= 30:
            cert['status'] = 'danger'
        elif progress >= 75:
            cert['status'] = 'on-track'
        elif progress >= 40:
            cert['status'] = 'behind'
        else:
            cert['status'] = 'danger'

        cert['id'] = doc.id
        certs.append(cert)

    return certs

def get_certificate(uid, cert_id):
    cert_ref = db.collection("users").document(uid).collection("certificates").document(cert_id)
    cert = cert_ref.get()
    if cert.exists:
        data = cert.to_dict()
        data['id'] = cert.id
        if 'renewal_date' in data and data['renewal_date']:
            data['renewal_date'] = data['renewal_date'].date()
        return data
    return None

def update_certificate(uid, cert_id, data):
    cert_ref = db.collection("users").document(uid).collection("certificates").document(cert_id)
    if 'renewal_date' in data and isinstance(data['renewal_date'], str):
        try:
            data['renewal_date'] = datetime.strptime(data['renewal_date'], '%Y-%m-%d')
        except ValueError:
            data['renewal_date'] = None
    cert_ref.update(data)

def delete_certificate(uid, cert_id):
    cert_ref = db.collection("users").document(uid).collection("certificates").document(cert_id)
    cert_ref.delete()


# ========================
# RECOMMENDATIONS COLLECTION (per user)
# ========================
def create_recommendation(uid, data):
    data['created_at'] = datetime.utcnow()
    ref = db.collection("users").document(uid).collection("recommendations").document()
    ref.set(data)
    return ref.id

def get_user_recommendations(uid):
    docs = db.collection("users").document(uid).collection("recommendations").stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def recommendation_to_dict(form, created_by_uid):
    return {
        "title": form.title.data,
        "description": form.description.data,
        "url": form.url.data,
        "expires_at": form.expires_at.data.strftime("%Y-%m-%d"),
        "created_by_uid": created_by_uid
    }

# ========================
# VERIFICATIONS COLLECTION (per user)
# ========================
def create_verification(uid, data):
    data['created_at'] = datetime.utcnow()
    ref = db.collection("users").document(uid).collection("verifications").document()
    ref.set(data)
    return ref.id

def get_user_verifications(uid):
    docs = db.collection("users").document(uid).collection("verifications").stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

# ========================
# NEWSLETTER
# ========================
def create_event(uid, data, event_type="general"):
    """
    data: dict with keys title, description, date, link, created_by_name
    event_type: "general", "newsletter", etc.
    """
    doc_ref = db.collection('events').document()
    to_store = {
        "id": doc_ref.id,
        "title": data.get("title"),
        "description": data.get("description"),
        "date": data.get("date") or None,
        "link": data.get("link") or None,
        "created_at": data.get("created_at") or datetime.utcnow(),
        "created_by_uid": uid,
        "created_by_name": data.get("created_by_name") or "",
        "type": event_type
    }
    doc_ref.set(to_store)
    return doc_ref.id

def get_all_events(limit=None, event_type=None):
    """
    Get all events, optionally filtered by type.
    """
    q = db.collection('events').order_by("created_at", direction=firestore.Query.DESCENDING)
    if event_type:
        q = q.where("type", "==", event_type)
    if limit:
        q = q.limit(limit)
    return [ {**d.to_dict(), "id": d.id} for d in q.stream() ]

def get_event(event_id):
    doc = db.collection('events').document(event_id).get()
    return {**doc.to_dict(), "id": doc.id} if doc.exists else None

def update_event(event_id, data):
    doc_ref = db.collection('events').document(event_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get('created_by_uid') != g.uid:
        return False
    doc_ref.update(data)
    return True

def delete_event(event_id):
    doc_ref = db.collection('events').document(event_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get('created_by_uid') != g.uid:
        return False
    doc_ref.delete()
    return True
    
# ========================
# CLEANUP FUNCTIONS
# ========================
def get_all_events(limit=None, event_type=None):
    """
    Get all events, optionally filtered by type.
    Auto-delete expired events based on their 'date' field.
    """
    now = datetime.utcnow()

    # Remove expired events
    expired_query = db.collection('events').where("date", "<", now)
    for doc in expired_query.stream():
        doc.reference.delete()

    # Fetch upcoming events
    q = db.collection('events').order_by("created_at", direction=firestore.Query.DESCENDING)
    if event_type:
        q = q.where("type", "==", event_type)
    if limit:
        q = q.limit(limit)
    return [{**d.to_dict(), "id": d.id} for d in q.stream()]

def get_user_recommendations(uid):
    now = datetime.utcnow()

    # Remove expired recommendations
    expired_query = db.collection("users").document(uid).collection("recommendations").where("expires_at", "<", now)
    for doc in expired_query.stream():
        doc.reference.delete()

    docs = db.collection("users").document(uid).collection("recommendations").stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]


