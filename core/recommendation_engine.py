from services.models import get_user_activities, create_recommendation
from datetime import datetime
from services.firebase_config import db
import requests
import os
import logging

# =====================
# RECOMMENDATION LOGIC
# =====================
def generate_recommendations(cert_name, cert_authority, uid=None):
    """
    Fetches recommendations from Firestore 'global_recommendations' collection
    based on matching tags or authority.
    """
    logger = logging.getLogger(__name__)
    recommendations = []

    cert_name = cert_name.lower() if cert_name else ""
    cert_authority = cert_authority.lower() if cert_authority else ""

    # 1. n8n Integration: Fetch Real-Time Data
    # Set N8N_WEBHOOK_URL in your environment variables
    n8n_url = os.environ.get('N8N_WEBHOOK_URL')
    if n8n_url:
        try:
            payload = {"cert_name": cert_name, "authority": cert_authority, "uid": uid}
            response = requests.post(n8n_url, json=payload, timeout=4)
            if response.status_code == 200:
                data = response.json()
                
                # Enterprise Data Normalization: Handle various n8n response formats
                raw_list = []
                if isinstance(data, list):
                    raw_list = data
                elif isinstance(data, dict):
                    # Check common keys used in n8n or API wrappers
                    raw_list = data.get('recommendations') or data.get('data') or data.get('items') or [data]
                
                # Filter out non-dict items and append
                if isinstance(raw_list, list):
                    valid_recs = [r for r in raw_list if isinstance(r, dict)]
                    recommendations.extend(valid_recs)
        except Exception as e:
            logger.error(f"n8n recommendation fetch failed: {e}")

    # 2. Fallback: Firestore & Static Criteria
    # Enterprise Approach: Query a curated collection in DB
    # We look for recommendations tagged with the authority or 'general'
    try:
        # 1. Fetch specific authority recommendations
        query = db.collection("global_recommendations").where("target_authority", "==", cert_authority).stream()
        for doc in query:
            recommendations.append(doc.to_dict())

        # Specific OffSec Criteria (based on CPE Handbook)
        if not recommendations and ("offsec" in cert_authority or "offensive security" in cert_authority):
            recommendations.extend([
                {
                    "title": "OffSec Proving Grounds (Labs)",
                    "url": "https://www.offsec.com/labs/",
                    "type": "lab",
                    "source": "OffSec",
                    "description": "Engage in hands-on labs. 1 CPE per hour of active engagement.",
                    "cpe": 1
                },
                {
                    "title": "Author a Security White Paper",
                    "url": "https://help.offsec.com/hc/en-us/articles/35366391096596",
                    "type": "research",
                    "source": "OffSec",
                    "description": "Write and publish a technical security paper (up to 40 CPEs).",
                    "cpe": 40
                },
                {
                    "title": "Develop Open Source Security Tool",
                    "url": "https://github.com/",
                    "type": "development",
                    "source": "Community",
                    "description": "Create or contribute significantly to a security tool (up to 40 CPEs).",
                    "cpe": 40
                }
            ])

        # 2. If empty, fetch general fallback
        if not recommendations:
            fallback = db.collection("global_recommendations").where("target_authority", "==", "general").limit(3).stream()
            for doc in fallback:
                recommendations.append(doc.to_dict())
    except Exception as e:
        logger.error(f"Error fetching global recommendations: {e}")

    # Store in Firestore only if uid is provided and no previous recommendations exist
    if uid:
        rec_ref = db.collection("users").document(uid).collection("recommendations")
        if not list(rec_ref.stream()):
            for rec in recommendations:
                rec_ref.add({**rec, "created_at": datetime.utcnow()})

    return recommendations