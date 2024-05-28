import os
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'partituras2024ubu')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'C:/Users/tomli/Desktop/gii/TFG_Partituras/Digitalizacion-Partituras/DigitalizacionPartiturasApp/partituras/uploaded_sheets'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    FIREBASE_CREDENTIALS = 'C:/Users/tomli/Desktop/gii/TFG_Partituras/Digitalizacion-Partituras/DigitalizacionPartiturasApp/sheet-transcribe-firebase-adminsdk-stggh-ac484e2751.json'
    # FIREBASE_CREDENTIALS = '/app/sheet-transcribe-firebase-adminsdk-stggh-ac484e2751.json'
    FIREBASE_BUCKET_NAME = 'sheet-transcribe.appspot.com'
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
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'true')

def configure_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myapp.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    if app.config.get('LOG_TO_STDOUT'):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Logging is set up.')
