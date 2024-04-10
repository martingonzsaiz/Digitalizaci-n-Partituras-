from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class SheetMusic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    pdf_path = db.Column(db.String(300))
    upload_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<SheetMusic {self.title}>'