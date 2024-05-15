from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
try:
    from config import Config, configure_logging
    # print("Configuración importada correctamente.")
except ImportError as e:
    print("Error al importar configuración:", e)
    
app = Flask(__name__)
# print("Aplicación Flask creada.")

try:
    app.config.from_object(Config)
    app.config['base_dir'] = Config.base_dir
    # print("Configuración cargada:")
    # print(app.config)  
    # print('Base dir:', app.config.get('base_dir'))  
except Exception as e:
    print("Error al cargar configuración:", e)

try:
    configure_logging(app)
    # print("Logging configurado.")
except Exception as e:
    print("Error al configurar logging:", e)
    
db = SQLAlchemy(app)
# print("SQLAlchemy inicializado.")

migrate = Migrate(app, db)
# print("Migrate configurado.")

login_manager = LoginManager(app)
login_manager.login_view = 'login'
# print("LoginManager configurado.")

try:
    from .models import User
    # print("Modelos importados correctamente.")
except ImportError as e:
    print("Error al importar modelos:", e)
    
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print("Error al cargar usuario:", e)

try:
    from . import routes
    # print("Rutas importadas correctamente.")
except ImportError as e:
    print("Error al importar rutas:", e)
