# services/firebase_config.py
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json

# Load Firebase credentials
# Priority: Environment Variable -> Local File
google_api_token = os.environ.get('GOOGLE_API_TOKEN')

if google_api_token:
    # Support both raw JSON string and file path in env var
    if google_api_token.strip().startswith('{'):
        cred_dict = json.loads(google_api_token)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(google_api_token)
else:
    # Fallback to local file for development
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
    if not os.path.exists(cred_path):
        raise FileNotFoundError("Firebase credentials not found. Set GOOGLE_API_TOKEN env var or provide serviceAccountKey.json.")
    cred = credentials.Certificate(cred_path)

# Initialize Firebase app
options = {}
storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET')
if storage_bucket:
    options['storageBucket'] = storage_bucket

firebase_admin.initialize_app(cred, options)

# Firestore DB client
db = firestore.client()
