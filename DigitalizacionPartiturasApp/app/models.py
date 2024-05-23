from datetime import datetime


class User:
    def __init__(self, username, email, passwordHash):
        self.username = username
        self.email = email
        self.passwordHash = passwordHash

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return f'<User {self.username}>'

class SheetMusic:
    def __init__(self, title, file_path, upload_date=None):
        self.title = title
        self.file_path = file_path
        self.upload_date = upload_date or datetime.now()

    def __repr__(self):
        return f'<SheetMusic {self.title}>'
