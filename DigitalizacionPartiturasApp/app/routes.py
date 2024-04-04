from flask import render_template, request, redirect, url_for
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
        if username == "admin" and password == "secret":  
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
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('¡Registro exitoso! Ahora puedes iniciar sesión.')
                return redirect(url_for('login'))
            else:
                return 'El nombre de usuario ya está en uso.'
    return render_template('register.html')

