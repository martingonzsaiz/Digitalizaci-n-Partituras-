from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'partituras2024ubu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@host.docker.internal/partituras_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/app/uploaded_sheets'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    GOOGLE_APPLICATION_CREDENTIALS = "/app/hip-transducer-422216-m7-5b7489d00ae2.json"
