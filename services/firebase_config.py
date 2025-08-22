# services/firebase_config.py
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Load Firebase credentials
# Make sure to put your serviceAccountKey.json in the project root
cred_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
cred_path = os.path.abspath(cred_path)

if not os.path.exists(cred_path):
    raise FileNotFoundError("Firebase serviceAccountKey.json not found. "
                            "Download it from Firebase Console > Project Settings > Service Accounts.")

cred = credentials.Certificate(cred_path)

# Initialize Firebase app
firebase_admin.initialize_app(cred)

# Firestore DB client
db = firestore.client()


