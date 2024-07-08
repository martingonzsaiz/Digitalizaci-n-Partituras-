# Importaciones de librerías y modulos
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.oauth2 import service_account
import json
import os
import base64

# Instancia de LoginManager para manejar la autenticación y gestión de sesiones
login_manager = LoginManager()

# Función para cargar credenciales
def load_credentials(info):
    credentials = service_account.Credentials.from_service_account_info(info)
    project = credentials.project_id
    return credentials, project

# Función para inicializar Firebase
def init_firebase(app):
    try:
        # Intento de obtener la app de Firebase si ya está inicializada
        firebase_admin.get_app()
    except ValueError:
        # Si Firebase no está inicializado, procedemos con la inicialización
        firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_JSON_BASE64', None)
        if not firebase_credentials_base64:
            raise ValueError("La variable de entorno FIREBASE_CREDENTIALS_JSON_BASE64 no está configurada.")
        
        # Decodificación de las credenciales y creación del objeto de credenciales
        cred_dict = json.loads(base64.b64decode(firebase_credentials_base64).decode('utf-8'))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': f"{cred_dict['project_id']}.appspot.com"
        })

    # Configuración del cliente de Firestore
    app.config['firestore_db'] = firestore.client()
    app.config['firebase_storage'] = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])
