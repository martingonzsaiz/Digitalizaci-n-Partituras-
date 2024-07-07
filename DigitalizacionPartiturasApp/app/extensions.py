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
    # Obtención de la credenciales de Firebase codificadas
    firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_JSON_BASE64', 'Variable no configurada')

    try:
        # Intento de obtener la app de Firebase
        firebase_admin.get_app()
    except ValueError:
        if not firebase_credentials_base64:
            raise ValueError("FIREBASE_CREDENTIALS_JSON_BASE64 no está configurado.")
        # Inicialización de Firebase con las credenciales
        cred_dict = json.loads(base64.b64decode(firebase_credentials_base64))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': f"{cred_dict['project_id']}.appspot.com"
        })

    # Configuración del cliente de Firestore
    app.config['firestore_db'] = firestore.client()
    
    # Configuración del bucket de Firebase Storage
    app.config['firebase_storage'] = storage.bucket()