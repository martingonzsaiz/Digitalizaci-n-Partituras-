from flask import render_template, request, redirect, url_for, flash
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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
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
            flash('Las contraseñas no coinciden.')
            return render_template('register.html')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user is None:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash('El usuario se ha registrado correctamente')
                return redirect(url_for('login'))
            else:
                flash('El nombre de usuario ya existe.')
                return render_template('register.html')
    else:
        return render_template('register.html')
