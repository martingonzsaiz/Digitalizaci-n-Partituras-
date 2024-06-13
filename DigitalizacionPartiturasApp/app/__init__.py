from flask import Flask
from flask_cors import CORS
from config import Config, configure_logging
from .extensions import login_manager, init_firebase
from .firebase_utils import get_user
from .models import User
from .routes import configure_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    login_manager.init_app(app)
    init_firebase(app)
    configure_logging(app)
    configure_routes(app)

    print(app.url_map)
    return app

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user(user_id)
    if user_data:
        return User(**user_data)
    return None
