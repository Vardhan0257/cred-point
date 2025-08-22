from services.models import get_user_activities, create_recommendation
from datetime import datetime
from services.firebase_config import db

# =====================
# RECOMMENDATION LOGIC
# =====================
def generate_recommendations(cert_name, cert_authority, uid=None):
    recommendations = []

    cert_name = cert_name.lower() if cert_name else ""
    cert_authority = cert_authority.lower() if cert_authority else ""

    # EC-Council-specific recommendations
    if "ec-council" in cert_authority or "ceh" in cert_name or "chfi" in cert_name:
        recommendations.extend([
            {
                "title": "Advanced CEH Training by EC-Council",
                "url": "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/",
                "type": "course",
                "source": "EC-Council",
                "description": "Deep dive into advanced penetration testing techniques aligned with CEH.",
                "cpe": 8
            },
            {
                "title": "Blue Team Operations Training",
                "url": "https://sans.org/blue-team",
                "type": "webinar",
                "source": "SANS Institute",
                "description": "Blue team incident response strategies. Valid for CEH CPEs.",
                "cpe": 5
            },
            {
                "title": "Cybersecurity Threat Intelligence eLearning",
                "url": "https://cybrary.it/course/cyber-threat-intelligence/",
                "type": "course",
                "source": "Cybrary",
                "description": "Earn CPEs while learning to identify and mitigate cyber threats.",
                "cpe": 6
            }
        ])
    else:
        # Default fallback recommendations
        recommendations.extend([
            {
                "title": "General Cybersecurity Awareness Training",
                "url": "https://www.cybrary.it/",
                "type": "course",
                "source": "Cybrary",
                "description": "Covers general security principles and best practices for any certification.",
                "cpe": 4
            },
            {
                "title": "Cloud Security Fundamentals",
                "url": "https://www.coursera.org/learn/cloud-security",
                "type": "course",
                "source": "Coursera",
                "description": "Intro to securing cloud environments. Counts towards CPE credits.",
                "cpe": 5
            }
        ])

    # Store in Firestore only if uid is provided and no previous recommendations exist
    if uid:
        rec_ref = db.collection("users").document(uid).collection("recommendations")
        if not list(rec_ref.stream()):
            for rec in recommendations:
                rec_ref.add({**rec, "created_at": datetime.utcnow()})

    return recommendations