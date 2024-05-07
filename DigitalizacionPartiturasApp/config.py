from datetime import timedelta
from google.cloud import storage
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'partituras2024ubu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/partituras_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/Users/tomli/Desktop/gii/TFG_Partituras/partituras/uploaded_sheets'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/tomli/Desktop/gii/TFG_Partituras/Digitalizacion-Partituras/DigitalizacionPartiturasApp/hip-transducer-422216-m7-5b7489d00ae2.json"

    client = storage.Client()
