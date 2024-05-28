from flask_login import LoginManager, UserMixin
from .firebase_utils import get_user

login_manager = LoginManager()
class User(UserMixin):
    def __init__(self, username, email, passwordHash):
        self.id = username
        self.email = email
        self.passwordHash = passwordHash
        
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

class SheetMusic:
    def __init__(self, title, file_path, upload_date=None):
        self.title = title
        self.file_path = file_path
        self.upload_date = upload_date
