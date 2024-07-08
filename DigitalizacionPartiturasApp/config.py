# Importaciones
import os
from datetime import timedelta
import logging
from logging.handlers import TimedRotatingFileHandler

# Clase de configuración de la aplicación
class Config:
    # Clave secreta utilizada para las sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY', 'partituras2024ubu')
    
    # Carpeta donde se guardan los archivos subidos
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/partituras/uploaded_sheets')
    
    # Duración de la sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Credenciales de Firebase codificadas en base64
    FIREBASE_CREDENTIALS_JSON_BASE64 = os.environ.get('FIREBASE_CREDENTIALS_JSON_BASE64')
    
    # Bucket de Firebase
    FIREBASE_BUCKET_NAME = os.environ.get('FIREBASE_BUCKET_NAME', 'sheet-transcribe.appspot.com')
    
    # Configuración de Firebase
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDWnvC205VEIMrRhwqgRavndvfAeiGkGaY",
        "authDomain": "sheet-transcribe.firebaseapp.com",
        "projectId": "sheet-transcribe",
        "storageBucket": "sheet-transcribe.appspot.com",
        "messagingSenderId": "842930665850",
        "appId": "1:842930665850:web:ecb1dbf50a0583be36fec3",
        "measurementId": "G-06V85QSKVF",
        "databaseURL": ""
    }
    
    # Variable de logs para stdout
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'true')

# Configuración del logging de la app
def configure_logging(app):
    
    # Si no existe logs se crean
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # Configuración para especificar la rotación de los logs cada día, el formato del mensaje y su nivel de logging
    file_handler = TimedRotatingFileHandler('logs/myapp.log', when='midnight')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Configuración de los logs para stdout enviandolos a un flujo
    if app.config.get('LOG_TO_STDOUT'):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    # Nivel del logger y mensaje
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Logging is set up.')
