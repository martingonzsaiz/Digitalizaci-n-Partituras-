from flask import Flask, Blueprint
from config import Config, configure_logging
from .extensions import migrate, login_manager, init_firebase
from .firebase_utils import get_user
from .models import User
from .routes import configure_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_firebase(app)
    migrate.init_app(app)
    login_manager.init_app(app)
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