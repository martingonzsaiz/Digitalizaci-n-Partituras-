import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'partituras2024ubu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/partituras_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/Users/tomli/Desktop/gii/TFG_Partituras/partituras/uploaded_sheets'
