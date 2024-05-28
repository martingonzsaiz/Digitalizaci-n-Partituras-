from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, initialize_app
import tempfile
import bcrypt
import subprocess
import os

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@main.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    firestore_db = current_app.config.get('firestore_db')
    if not firestore_db:
        flash('Error de conexión', 'error')
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ref = firestore_db.collection('users').document(username)
        user_snapshot = user_ref.get()

        if user_snapshot.exists:
            user_data = user_snapshot.to_dict()
            if bcrypt.checkpw(password.encode('utf-8'), user_data['passwordHash'].encode('utf-8')):
                user = User(username=user_data['username'], email=user_data['email'], passwordHash=user_data['passwordHash'])
                login_user(user, remember=False)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.menu'))
            else:
                flash('Usuario o contraseña inválida', 'error')
        else:
            flash('Usuario no encontrado', 'error')

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    firestore_db = current_app.config.get('firestore_db')
    if not firestore_db:
        current_app.logger.error("Firestore DB no es accesible.")
        flash('Error de conexión', 'error')
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        password2 = request.form['password2']

        if not email:
            flash('El email es obligatorio.', 'error')
            return render_template('register.html')

        if password != password2:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')

        user_ref = firestore_db.collection('users').document(username)
        user_snapshot = user_ref.get()
        if user_snapshot.exists:
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('register.html')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_ref.set({
            'username': username,
            'email': email,
            'passwordHash': hashed_password
        })
        flash('El usuario se ha registrado correctamente', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/menu', methods=['GET'])
@login_required
def menu():
    return render_template('menu.html')

def digitalize_sheets(file_path):
    batch_script = os.path.join('C:/Users/tomli/Desktop/gii/TFG_Partituras/Digitalizacion-Partituras/DigitalizacionPartiturasApp/audiveris/build/distributions/Audiveris-5.3.1/bin', 'run_audiveris.bat')
    # batch_script = os.path.join('app/audiveris', 'run_audiveris.bat')

    cmd = [batch_script, file_path]
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Partitura digitalizada correctamente:", result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print("Error durante la digitalización:", e.stderr.decode('utf-8'))

    except Exception as e:
        current_app.logger.error("Otro error al digitalizar la partitura: %s", str(e))
        
def allowed_file(filename):
    return filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            user_folder = f'user_{current_user.get_id()}/'
            file_type_folder = 'pdf/' if filename.endswith('.pdf') else 'images/'
            full_path = f'partituras/{user_folder}{file_type_folder}{filename}'

            blob = current_app.config['firebase_storage'].blob(full_path)
            blob.upload_from_file(file.stream, content_type=file.content_type)
            flash('Partitura subida correctamente.')
            return redirect(url_for('main.menu'))  

    return render_template('upload.html')

def download_sheets(bucket_name, file_name):
    username = current_user.get_id()
    file_extension = file_name.split('.')[-1]
    if file_extension in ['pdf']:
        file_type_folder = 'pdf'
    elif file_extension in ['png', 'jpg', 'jpeg']:
        file_type_folder = 'images'
    full_blob_name = f"partituras/user_{username}/{file_type_folder}/{file_name}"

    if not firebase_admin._apps:
        cred_path = current_app.config['FIREBASE_CREDENTIALS']
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        cred = firebase_admin.get_app().credential.get_credential()

    storage_client = storage.Client(credentials=cred, project=cred.project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(full_blob_name)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')

    blob.download_to_filename(temp_file.name)
    temp_file.close()  
    print('Archivo descargado en:', temp_file.name)
    # temp_dir = tempfile.gettempdir()
    
    # temp_contents = os.listdir(temp_dir)
    
    # full_paths = [os.path.join(temp_dir, file) for file in temp_contents]

    # for item in full_paths:
    #     print(item)
    return temp_file.name

@main.route('/digitalize', methods=['POST'])
@login_required
def digitalize():
    filename = request.form['filename']
    input_file_path = download_sheets(current_app.config['FIREBASE_BUCKET_NAME'], filename)
    print(input_file_path)
    digitalize_sheets(input_file_path)
    flash('Partitura digitalizada correctamente.')
    return redirect(url_for('main.list_sheet_music'))

@main.route('/list_sheet_music', methods=['GET'])
@login_required
def list_sheet_music():
    try:
        user_folder = f'partituras/user_{current_user.get_id()}/pdf/'  
        bucket = current_app.config['firebase_storage']
        
        sheet_music_files = []

        blobs = bucket.list_blobs(prefix=user_folder)
        for blob in blobs:
            if allowed_file(blob.name):
                download_url = blob.generate_signed_url(expiration=timedelta(minutes=5))  
                file_name = blob.name[len(user_folder):]
                sheet_music_files.append({'name': file_name, 'url': download_url})
        
    except Exception as e:
        current_app.logger.error(f"Error al listar las partituras: {str(e)}")
        flash(f"Error al listar las partituras: {str(e)}")

    return render_template('list_sheet_music.html', sheet_music_files=sheet_music_files)


def configure_routes(app):
    app.register_blueprint(main)
