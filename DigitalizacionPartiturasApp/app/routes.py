from flask import render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, login_required, logout_user
from app.models import User
from werkzeug.utils import secure_filename
import os
from app.models import SheetMusic
from app import app, db

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user, remember=False)
            return redirect(url_for('menu'))
        else:
            return 'Usuario o contraseña inválida'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))

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
    
@app.route('/menu', methods=['GET'])
@login_required
def menu():
        return render_template('menu.html')
    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        pdf = request.files['pdf']

        if pdf and allowed_file(pdf.filename):
            filename = secure_filename(pdf.filename)
            pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            pdf.save(pdf_path)

            new_sheetmusic = SheetMusic(title=title, pdf_path=pdf_path)
            db.session.add(new_sheetmusic)
            db.session.commit()
            flash('Partitura subida correctamente!')
            return redirect(url_for('home'))

    return render_template('upload.html')

def allowed_file(filename):
    return filename.lower().endswith('.pdf')

