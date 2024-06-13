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

def load_credentials_from_info(info):
    credentials = service_account.Credentials.from_service_account_info(info)
    project = credentials.project_id
    return credentials, project

def init_firebase(app):
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')
        if not firebase_credentials_base64:
            raise ValueError("La variable de entorno FIREBASE_CREDENTIALS_JSON no está configurada o está vacía.")
        
        cred_dict = json.loads(base64.b64decode(firebase_credentials_base64).decode('utf-8'))
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': f"{cred_dict['project_id']}.appspot.com"
        })
    
    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket()
