from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app import app, db

@app.route('/')
def home():
    return 'Página Principal'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return redirect(url_for('home'))
        else:
            return 'Usuario o contraseña inválida'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        
        if password != password2:
            return 'Las contraseñas no coinciden.'
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user is None:
                new_user = User(username=username, password_hash=password)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('El usuario se ha registrado correctamente')
                return redirect(url_for('login'))
            else:
                return 'El nombre de usuario ya existe.'
    return render_template('register.html')

