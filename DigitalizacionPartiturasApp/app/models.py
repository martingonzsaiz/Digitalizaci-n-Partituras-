from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print(f"Generated hash: {self.password_hash}")


    def check_password(self, password):
        result = check_password_hash(self.password_hash, password)
        print(f"Checking password: {password} against hash: {self.password_hash}. Result: {result}")
        return check_password_hash(self.password_hash, password)
        