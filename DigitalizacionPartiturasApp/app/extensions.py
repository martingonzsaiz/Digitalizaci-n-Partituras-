import os
import json
import base64
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore, storage

login_manager = LoginManager()

def init_firebase(app):
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')
        if not firebase_credentials_base64:
            raise ValueError("La variable de entorno FIREBASE_CREDENTIALS_JSON no está configurada.")
        
        try:
            cred_dict = json.loads(base64.b64decode(firebase_credentials_base64).decode('utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError("La cadena base64 decodificada no es un JSON válido.") from e
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': app.config['FIREBASE_BUCKET_NAME']
        })

    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])
