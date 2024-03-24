from app import app
from flask import render_template, request, redirect, url_for

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

