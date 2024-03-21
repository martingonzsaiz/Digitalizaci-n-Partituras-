import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'partituras2024ubu'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tu_base_de_datos.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
