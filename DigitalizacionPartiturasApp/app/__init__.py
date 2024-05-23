from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import current_app
from config import Config, configure_logging
from firebase_admin import credentials, initialize_app, firestore, storage
from .routes import configure_routes
from .models import User
import pyrebase
import logging

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    configure_logging(app)

    init_login(app)
    db.init_app(app)
    migrate.init_app(app, db)
    init_firebase(app)

    configure_routes(app)

    return app

def init_login(app):
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

def init_firebase(app):
    creds_path = app.config['FIREBASE_CREDENTIALS']
    cred = credentials.Certificate(creds_path)
    firebase_admin = initialize_app(cred, {'storageBucket': app.config['FIREBASE_BUCKET_NAME']})

    firestore_db = firestore.client()
    
    firebase_bucket = storage.bucket(app.config['FIREBASE_BUCKET_NAME'])

    firebase_config = app.config['FIREBASE_CONFIG']
    firebase_app = pyrebase.initialize_app(firebase_config)
    firebase_db = firebase_app.database()
    auth = firebase_app.auth()

    app.config['firestore_db'] = firestore_db
    app.config['firebase_db'] = firebase_db
    app.config['firebase_auth'] = auth
    app.config['firebase_storage'] = firebase_bucket

    logging.info("Firebase se ha inicializado correctamente.")
    
@login_manager.user_loader
def load_user(user_id):
    firestore_db = current_app.config.get('firestore_db')
    if not firestore_db:
        current_app.logger.error("Firestore DB no es accesible para el usuario.")
        return None

    user_ref = firestore_db.collection('users').document(user_id)
    user_snapshot = user_ref.get()
    if user_snapshot.exists:
        user_data = user_snapshot.to_dict()
        return User(username=user_data['username'], email=user_data['email'], passwordHash=user_data['passwordHash'])
    else:
        return None

