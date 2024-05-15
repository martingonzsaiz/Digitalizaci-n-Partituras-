import sys
from flask import current_app, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user
import subprocess
import os
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, SheetMusic
from google.cloud import storage

def create_storage_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = current_app.config['GOOGLE_APPLICATION_CREDENTIALS']
    return storage.Client()

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

def digitalize_sheet_music(input_dir):
    output_dir = current_app.config['AUDIVERIS_OUTPUT']
    audiveris_bat = 'C:\\Users\\tomli\\Desktop\\gii\\TFG_Partituras\\Digitalizacion-Partituras\\DigitalizacionPartiturasApp\\audiveris\\build\\distributions\\Audiveris-5.3.1\\bin\\Audiveris.bat'
    
    cmd = [
        audiveris_bat,
        '-batch', '-export',
        '-output', output_dir,
        '--', input_dir
    ]
    
    print("Comando a ejecutar:", cmd, file=sys.stdout)
    current_app.logger.debug("Comando a ejecutar: %s", cmd)

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        current_app.logger.info("Partitura digitalizada correctamente: %s", result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        current_app.logger.error("Error durante la digitalización: %s", e.stderr.decode('utf-8'))
    except Exception as e:
        current_app.logger.error("Otro error al digitalizar la partitura: %s", str(e))

def allowed_file(filename):
    return filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_file_path = os.path.join(current_app.config['AUDIVERIS_INPUT'], filename)
            file.save(temp_file_path)

            flash('Partitura subida correctamente.')
            return redirect(url_for('menu'))  

    return render_template('upload.html')

@app.route('/digitalize', methods=['POST'])
@login_required
def digitalize():
    filename = request.form['filename']
    input_dir = os.path.join(current_app.config['AUDIVERIS_INPUT'], filename)

    try:
        digitalize_sheet_music(input_dir)
        flash('Partitura digitalizada correctamente.')
    except Exception as e:
        flash(f"Error durante la digitalización: {str(e)}")

    return redirect(url_for('list_sheet_music'))

@app.route('/list_sheet_music', methods=['GET'])
@login_required
def list_sheet_music():
    input_folder = current_app.config['AUDIVERIS_INPUT']
    try:
        sheet_music_files = os.listdir(input_folder)
        sheet_music_files = [f for f in sheet_music_files if allowed_file(f)]
    except Exception as e:
        flash(f"Error al listar las partituras: {str(e)}")
        sheet_music_files = []

    return render_template('list_sheet_music.html', sheet_music_files=sheet_music_files)
