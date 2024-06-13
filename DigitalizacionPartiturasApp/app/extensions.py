import firebase_admin
from firebase_admin import credentials, initialize_app, firestore, storage
import json
import os

def init_firebase(app):
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS_JSON', '{}'))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': app.config['FIREBASE_BUCKET_NAME']
        })

    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])
