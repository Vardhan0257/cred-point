from services.models import get_user_activities, create_verification
from datetime import datetime

# =====================
# VERIFICATION LOGIC
# =====================
def verify_activities(uid):
    """
    Loops through user activities and auto-verifies them based on simple rules.
    Saves verification results in Firestore.
    """
    activities = get_user_activities(uid)
    verifications = []

    for activity in activities:
        verification_status = "pending"

        # Example rule: auto-verify if activity has a provider & CPE points > 0
        if activity.get("provider") and int(activity.get("cpe_points", 0)) > 0:
            verification_status = "verified"

        verif_record = {
            "activity_id": activity.get("id") or activity.get("activity_id"),
            "status": verification_status,
            "user_id": uid,
            "verified_at": datetime.utcnow() if verification_status == "verified" else None
        }

        # Save to Firestore
        create_verification(uid, verif_record)
        verifications.append(verif_record)

    return verifications
