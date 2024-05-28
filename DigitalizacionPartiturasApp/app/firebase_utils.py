import firebase_admin
from firebase_admin import firestore

def get_db():
    return firestore.client(app=firebase_admin.get_app())

def create_user(username, email, password_hash):
    db = get_db()
    user_ref = db.collection('users').document(username)
    user_ref.set({
        'username': username,
        'email': email,
        'passwordHash': password_hash
    })

def get_user(username):
    db = get_db()
    user_ref = db.collection('users').document(username)
    doc = user_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None
