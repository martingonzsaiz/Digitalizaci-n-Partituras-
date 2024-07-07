# Importaciones de modulos y librerías
from flask import Flask
from flask_cors import CORS
from config import Config, configure_logging
from .extensions import login_manager, init_firebase
from .firebase_utils import get_user
from .models import User
from .routes import configure_routes

def create_app():
    # Creación de una instancia de la aplicación de Flask
    app = Flask(__name__)
    
    # Habilitación de CORS en la aplicación
    CORS(app)
    
    # Configuración obtenida del modulo config
    app.config.from_object(Config)


    # Inicialización de login_manager
    login_manager.init_app(app)
    
    # Inicialización de Firebase
    init_firebase(app)
    
    # Configuración de los logs
    configure_logging(app)
    
    # Configuración de las rutas de la app
    configure_routes(app)

    # Retorno de la app preparada y configurada
    return app

#Creación de la app
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    # Obtención de los datos del usuario desde Firebase
    user_data = get_user(user_id)
    
    # Si el usuario existe, se devuelve una instancia recien creada
    if user_data:
        return User(**user_data)
    return None