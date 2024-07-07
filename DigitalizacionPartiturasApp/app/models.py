# Importación de modulos y librerías
from flask_login import LoginManager, UserMixin
import bcrypt
from .firebase_utils import get_user

# Instancia de LoginManager para manejar la autenticación y gestión de sesiones
login_manager = LoginManager()

# Clase User que hereda UserMixin para la gestión de usuarios
class User(UserMixin):
    
    # Constructor de la clase
    def __init__(self, username, email, passwordHash):
        self.id = username
        self.email = email
        self.password_hash = passwordHash

    # Método para autenticar usuarios encriptando las contraseñas
    @staticmethod
    def authenticate(username, password, db):
        user_data = db.get_user(username)
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            return User(**user_data)
        return None

# Clase SheetMusic que representa a las partituras
class SheetMusic:
    
    # Constructor de la clase
    def __init__(self, title, file_path, upload_date=None):
        self.title = title
        self.file_path = file_path
        self.upload_date = upload_date