from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.oauth2 import service_account
import json
import os
import base64

login_manager = LoginManager()

def load_credentials_from_file(file_path):
    credentials = service_account.Credentials.from_service_account_file(file_path)
    project = credentials.project_id
    return credentials, project

def init_firebase(app):
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_dict = json.loads(base64.b64decode(os.environ.get('FIREBASE_CREDENTIALS_JSON', '')).decode('utf-8'))
        with open('temp_firebase_credentials.json', 'w') as temp_cred_file:
            json.dump(cred_dict, temp_cred_file)

        cred_path = 'temp_firebase_credentials.json'
        cred, project = load_credentials_from_file(cred_path)

        firebase_admin.initialize_app(cred, {
            'storageBucket': app.config['FIREBASE_BUCKET_NAME']
        })

    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])
