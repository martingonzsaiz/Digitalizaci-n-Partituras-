import base64
import json
import os
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore, storage

login_manager = LoginManager()

def init_firebase(app):
    try:
        firebase_admin.get_app()
    except ValueError:
        try:
            cred_dict = json.loads(base64.b64decode(os.environ.get('FIREBASE_CREDENTIALS_JSON', '')).decode('utf-8'))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': app.config['FIREBASE_BUCKET_NAME']
            })
        except json.JSONDecodeError as e:
            app.logger.error(f"Error decoding JSON: {str(e)}")
            raise

    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])
