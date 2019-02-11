"""Used to configure and setup Cloud Firestore instance."""
# External imports
import firebase_admin
from firebase_admin import firestore
# Internal imports
import utils

CREDENTIALS = firebase_admin.credentials.Certificate(
    utils.create_file_path('data/api_keys/firebase_key.json'))
firebase_admin.initialize_app(CREDENTIALS)

def configure_cloud_firestore():
    """Returns a firebase cloud firestore instance."""
    return firestore.client()
