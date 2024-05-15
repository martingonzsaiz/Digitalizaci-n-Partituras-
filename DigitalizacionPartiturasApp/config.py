from datetime import timedelta
import os
import logging
from logging.handlers import RotatingFileHandler

class Config:
    base_dir = 'C:/Users/tomli/Desktop/gii/TFG_Partituras/Digitalizacion-Partituras/DigitalizacionPartiturasApp'
    print("Base dir desde config:", base_dir)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'partituras2024ubu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/partituras_db'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@host.docker.internal/partituras_db' Configuración para el docker
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(base_dir, 'partituras', 'uploaded_sheets')
    # UPLOAD_FOLDER = '/app/uploaded_sheets' Configuración para el docker 
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    # GOOGLE_APPLICATION_CREDENTIALS = "/app/hip-transducer-422216-m7-5b7489d00ae2.json" Configuración para el docker
    GOOGLE_APPLICATION_CREDENTIALS = os.path.join(base_dir, "hip-transducer-422216-m7-5b7489d00ae2.json")
    # AUDIVERIS_INPUT = '/app/audiveris_input' Configuración para el docker 
    AUDIVERIS_INPUT = os.path.join(base_dir, 'audiveris_input')
    AUDIVERIS_OUTPUT = os.path.join(base_dir, 'audiveris_output')
    EXECUTABLE_PATH = os.path.join(base_dir, 'audiveris', 'build', 'distributions', 'Audiveris-5.3.1', 'bin', 'Audiveris')
    JAVA_EXECUTABLE = "java"
    AUDIVERIS_CLASSPATH = os.path.join(base_dir, 'audiveris', 'build', 'distributions', 'Audiveris-5.3.1', 'lib', '*')

def configure_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myapp.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
