from services.models import get_user_activities, create_verification, update_activity
from datetime import datetime


# Lightweight grading rules based on OffSec handbook (simplified):
# - course: 1 CPE per hour, cap 40 for typical course mapping
# - webinar/conference: 1 CPE per hour
# - public_speaking / published_paper: fixed 4 CPEs per event/paper
# - lab_submission: 20 CPEs if accepted (external acceptance required)

def grade_activity(activity):
    """Return (awarded_cpe:int/float or None, reason:str, auto_approved:bool)."""
    atype = (activity.get('activity_type') or '').lower()
    src = (activity.get('submission_source') or '').lower()
    dur = activity.get('duration_hours')

    # If already awarded, return existing
    if activity.get('awarded_cpe') is not None:
        return activity.get('awarded_cpe'), 'already_awarded', True

    # Course: 1 CPE per hour, cap 40
    if atype == 'course':
        if dur:
            awarded = float(dur)
            if awarded > 40:
                awarded = 40.0
            return awarded, f'course_{awarded}_hours', True
        # If no duration provided, pending manual review
        return None, 'course_missing_duration', False

    if atype in ('webinar', 'conference'):
        if dur:
            awarded = float(dur)
            return awarded, f'{atype}_{awarded}_hours', True
        return None, f'{atype}_missing_duration', False

    if atype == 'public_speaking' or atype == 'published_paper':
        # Fixed award per item; quick auto-approve if evidence exists
        evidence = activity.get('proof_file') or activity.get('evidence_paths')
        if evidence:
            return 4.0, f'{atype}_standard', True
        return None, f'{atype}_no_evidence', False

    if atype == 'lab_submission':
        # require acceptance flag for auto-approval
        accepted = activity.get('accepted') or False
        if accepted:
            return 20.0, 'lab_submission_accepted', True
        return None, 'lab_submission_pending_acceptance', False

    # Default: if user provided explicit cpe_points and proof exists, accept it
    if activity.get('cpe_points') is not None:
        if activity.get('proof_file') or activity.get('evidence_paths'):
            return float(activity.get('cpe_points')), 'user_provided_with_evidence', True
        return None, 'user_provided_no_evidence', False

    return None, 'unable_to_grade', False


def verify_activities(uid):
    """Grade and create verification records for a user's activities."""
    activities = get_user_activities(uid) or []
    verifications = []

    for activity in activities:
        activity_id = activity.get('id') or activity.get('activity_id')
        awarded_cpe, reason, auto = grade_activity(activity)

        status = 'verified' if awarded_cpe is not None and auto else 'pending'

        verif_record = {
            'activity_id': activity_id,
            'status': status,
            'user_id': uid,
            'awarded_cpe': awarded_cpe,
            'reason': reason,
            'auto_approved': bool(auto),
            'verified_at': datetime.utcnow() if status == 'verified' else None
        }

        # persist verification record
        create_verification(uid, verif_record)
        verifications.append(verif_record)

        # update activity doc with awarded values if approved
        if awarded_cpe is not None and auto:
            try:
                update_activity(uid, activity_id, {
                    'awarded_cpe': awarded_cpe,
                    'awarded_reason': reason,
                    'status': 'approved',
                    'updated_at': datetime.utcnow()
                })
            except Exception:
                # best-effort: continue
                pass

    return verifications
