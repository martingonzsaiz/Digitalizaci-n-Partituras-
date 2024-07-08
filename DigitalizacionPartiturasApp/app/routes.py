# Importaciones de librerías y modulos
from datetime import timedelta
from datetime import datetime
import json
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import load_credentials
from .models import SheetMusic, User
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore
import zipfile
import base64
import tempfile
import bcrypt
import subprocess
import os
import google.api_core.exceptions
from pdf2image import convert_from_path
import cv2
import numpy as np
import io
from os import listdir

# Blueprint para organizar las rutas
main = Blueprint('main', __name__, template_folder='templates')

# Ruta de la pagina de inicio
@main.route('/', methods=['GET'])
def index():
    return render_template('home.html')

# Ruta de la pagina principal
@main.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

# Ruta del inicio de sesión
@main.route('/login', methods=['GET', 'POST'])
def login():
    # Obtención de la base de datos de Firestore
    firestore_db = current_app.config.get('firestore_db')
    if not firestore_db:
        flash('Error de conexión', 'error')
        return render_template('login.html')

    if request.method == 'POST':
        # Obtención de las credenciales
        username = request.form['username']
        password = request.form['password']

        # Referencia al usuario en Firestore
        user_ref = firestore_db.collection('users').document(username)
        user_snapshot = user_ref.get()

        # Comprobación de la existencia de un usuario y sus credenciales y lo autentica
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

# Ruta del cierre de sesión
# Requiere haber iniciado sesión
@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Obtención de la base de datos de Firestore
    firestore_db = current_app.config.get('firestore_db')
    if not firestore_db:
        flash('Error de conexión', 'error')
        return render_template('register.html')

    if request.method == 'POST':
        # Datos del formulario
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        password2 = request.form['password2']

        # Validaciones del formulario
        if not email:
            flash('El email es obligatorio.', 'error')
            return render_template('register.html')
        if password != password2:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')

        # Comprobación de si el correo electrónico ya está en uso
        users_ref = firestore_db.collection('users')
        existing_email_query = [doc for doc in users_ref.where('email', '==', email).stream()]
        if existing_email_query:
            flash('Este correo electrónico ya está registrado.', 'error')
            return render_template('register.html')

        # Referencia al documento del usuario
        user_ref = firestore_db.collection('users').document(username)
        user_snapshot = user_ref.get()
        
        # Comprobación de si el documento del usuario ya existe
        if user_snapshot.exists:
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('register.html')
        
        # Hasheo de contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Registro del usuario en Firestore
        user_ref.set({
            'username': username,
            'email': email,
            'passwordHash': hashed_password
        })
        flash('El usuario se ha registrado correctamente', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Ruta para el menu
# Requiere haber iniciado sesión
@main.route('/menu', methods=['GET'])
@login_required
def menu():
    return render_template('menu.html')

def digitalize_sheets(file_path, sheet_music):
    # Directorio de salida para los archivos digitalizados
    output_dir = '/app/audiveris_output'
    
    # Limpieza del directorio antes de la digitalización
    clean_directory(output_dir)
    
    # Ruta del script de ejecución de Audiveris
    batch_script = '/app/run_audiveris.sh'
    
    # Crea la lista de comandos para ejecutar el script de Audiveris con la ruta del archivo de partitura
    cmd = [batch_script, file_path]
        
    try:
        # Ejecución del comando
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            # Mensaje de error si el comando falló
            flash(f"Error durante la digitalización: {result.stderr}", 'error')
            return None, output_dir

        # Registro del archivo de log en el directorio de salida
        log_file = find_log_file(output_dir)
        
        # Comprobación del archivo de log
        if log_file is None:
            current_app.logger.error("No se encontró el archivo de log en el directorio: {}".format(output_dir))
            flash("No se encontró el archivo de log.", 'error')
            return None, output_dir

        # Análisis del log
        is_valid, message = analyze_audiveris_log(log_file)
        # Comprobación de errores
        if not is_valid:
            current_app.logger.error(f"Error en log de Audiveris: {message}")
            flash(message, 'error')
            return None, output_dir

        # Listado de los archivos MXL
        mxl_files = [file for file in os.listdir(output_dir) if file.endswith('.mxl')]
        current_app.logger.info(f"Archivos MXL encontrados: {mxl_files}")
        if not mxl_files:
            # Mensaje de error si no se encontraron archivos MXL
            flash("Error de digitalización: No se encontró ningún archivo MXL.", 'error')
            return None, output_dir

        return os.path.join(output_dir, mxl_files[0]), output_dir

    # Manejo de excepciones de subprocess
    except subprocess.CalledProcessError as e:
        flash(f"Error durante la digitalización: {e.stderr}", 'error')
        return None, output_dir
    except Exception as e:
        flash(f"Error al ejecutar Audiveris: {str(e)}", 'error')
        return None, output_dir

# Busqueda del archivo log en un directorio
def find_log_file(directory):
    log_files = [f for f in os.listdir(directory) if f.endswith('.log')]
    if log_files:
        latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
        return os.path.join(directory, latest_log)
    return None

# Análisis de un archivo log mediante cadenas de caracteres
def analyze_audiveris_log(log_file_path):
    try:
        with open(log_file_path, 'r') as file:
            log_contents = file.read()
        
        if "the picture resolution is too low" in log_contents:
            return False, "La resolución de la imagen es demasiado baja."
        if "this sheet contains no staves" in log_contents:
            return False, "La partitura no contiene pentagramas visibles."
        if "invalid sheet" in log_contents:
            return False, "Hoja inválida detectada."

        return True, "Digitalización completada sin errores detectados."

    except FileNotFoundError:
        return False, "Archivo de log no encontrado."
    except Exception as e:
        return False, f"Error al leer el archivo de log: {str(e)}"

# Función de formatos de partituras permitidos
def allowed_file(filename):
    return filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg','.mxl'))

# Comprobación de la autorización del usuario
def is_user_authorized(file_path):
    firestore_db = current_app.config['firestore_db']
    user_id = current_user.get_id()
    query_result = firestore_db.collection('sheet_music').where('file_path', '==', file_path).where('username', '==', user_id).get()
    return len(query_result) > 0

# Ruta para subir una partitura
# Requiere haber iniciado sesión
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Archivo de la solicitud
        file = request.files['file']
        # Título de la partitura
        title = request.form['title']
        # Comprobación de la existencia del archivo y su formato
        if file and allowed_file(file.filename):
            # Comprobación de la seguridad del archivo
            original_filename = secure_filename(file.filename)
            
            # Extensión del archivo
            extension = os.path.splitext(original_filename)[1]
            filename = secure_filename(title) + extension
            
            # Definición de las carpetas en función del usuario
            user_folder = f'user_{current_user.get_id()}/'
            
            # Determinación el directorio correcto
            if extension == '.mxl':
                file_type_folder = 'mxl/'
                collection_name = 'digitalized_sheets'
            elif extension in ['.pdf', '.png', '.jpg', '.jpeg']:
                file_type_folder = extension.replace('.', '') + '/'
                collection_name = 'sheet_music'
            else:
                file_type_folder = 'others/'
                collection_name = 'sheet_music'

            full_path = f'partituras/{user_folder}{file_type_folder}{filename}'

            # Subir archivo y registro en Firestore
            blob = current_app.config['firebase_storage'].blob(full_path)
            blob.upload_from_file(file.stream, content_type=file.content_type)

            firestore_db = current_app.config['firestore_db']
            firestore_db.collection(collection_name).document(filename).set({
                'title': title,
                'file_path': full_path,
                'upload_date': datetime.now(),
                'username': current_user.get_id()
            })
            flash('Partitura subida correctamente.')
            return redirect(url_for('main.menu'))
    return render_template('upload.html')

# Ruta para eliminar una partitura
# Requiere haber iniciado sesión
@main.route('/delete_sheet/<doc_id>', methods=['POST'])
@login_required
def delete_sheet(doc_id):
    try:
        firestore_db = current_app.config['firestore_db']
        # Referencia a la partitura de la colección
        doc_ref = firestore_db.collection('sheet_music').document(doc_id)
        # Documento de Firestore
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()['username'] == current_user.get_id():
            file_details = doc.to_dict()
            file_path = file_details['file_path']

            # Obtención del objeto blob y eliminación del archivo
            blob = current_app.config['firebase_storage'].blob(file_path)
            blob.delete()

            # Eliminación del documento
            doc_ref.delete()
            flash('Partitura eliminada correctamente.', 'success')
        else:
            flash('No autorizado para eliminar esta partitura o partitura inexsitente.', 'error')
    # Excepciones
    except Exception as e:
        current_app.logger.error(f"Error al eliminar la partitura: {str(e)}")
        flash(f'Error al eliminar la partitura: {str(e)}', 'error')

    return redirect(url_for('main.list_sheet_music'))

# Ruta para eliminar una partitura digitalizada
# Requiere haber iniciado sesión
@main.route('/delete_digitalized_sheet/<doc_id>', methods=['POST'])
@login_required
def delete_digitalized_sheet(doc_id):
    try:
        firestore_db = current_app.config['firestore_db']
        doc_ref = firestore_db.collection('digitalized_sheets').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()['username'] == current_user.get_id():
            file_details = doc.to_dict()
            file_path = file_details['file_path']

            blob = current_app.config['firebase_storage'].blob(file_path)
            blob.delete()

            doc_ref.delete()
            flash('Partitura digitalizada eliminada correctamente.', 'success')
        else:
            flash('No se encontró la partitura digitalizada especificada.', 'error')
    except Exception as e:
        current_app.logger.error(f"Error al eliminar la partitura digitalizada: {str(e)}")
        flash(f'Error al eliminar la partitura digitalizada: {str(e)}', 'error')

    return redirect(url_for('main.list_digitalized_sheets'))

# Función para descargar partituras
def download_sheets(bucket_name, file_name):
    # Nombre del archivo y su extensión
    filename_only = file_name.split('/')[-1]
    file_extension = filename_only.split('.')[-1].lower()
    file_type_folder = file_extension
    
    # Id del usuario actual
    username = current_user.get_id()
    full_blob_name = f"partituras/user_{username}/{file_type_folder}/{filename_only}"
    current_app.logger.info(f"Descargando archivo desde Firebase: {full_blob_name}")

    try:
        # Obtención de las credenciales de Firebase desde la variable de entorno
        firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_JSON_BASE64', '')
        if not firebase_credentials_base64:
            raise ValueError("La variable de entorno FIREBASE_CREDENTIALS_JSON_BASE64 no está configurada o está vacía.")
        
        # Decodificación y carga de las credenciales
        cred_dict = json.loads(base64.b64decode(firebase_credentials_base64).decode('utf-8'))
        credentials, project = load_credentials(cred_dict)

        storage_client = storage.Client(credentials=credentials, project=project)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(full_blob_name)
        
        # Archivo temporal para la descarga
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
        blob.download_to_filename(temp_file.name)

        current_app.logger.info(f'Archivo descargado: {temp_file.name}')
        return temp_file.name

    # Excepciones
    except google.api_core.exceptions.NotFound:
        current_app.logger.error(f"Archivo no encontrado: {full_blob_name}")
        flash("Archivo no encontrado.", 'error')
        return None
    except Exception as e:
        current_app.logger.error(f"Error al descargar el archivo: {str(e)}")
        flash("Error al descargar el archivo.", 'error')
        return None

# Ruta para descargar una partitura
# Requiere haber iniciado sesión
@main.route('/download_sheet/<doc_id>', methods=['GET'])
@login_required
def download_sheet(doc_id):
    try:
        firestore_db = current_app.config['firestore_db']
        doc_ref = firestore_db.collection('digitalized_sheets').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict()['username'] == current_user.get_id():
            file_details = doc.to_dict()
            file_path = file_details['file_path']
            blob = current_app.config['firebase_storage'].blob(file_path)
            file_obj = io.BytesIO()
            blob.download_to_file(file_obj)
            file_obj.seek(0)
            return send_file(
                file_obj,
                as_attachment=True,
                download_name=file_path.split('/')[-1],
                mimetype='application/octet-stream'
            )
        else:
            flash('No se encontró la partitura especificada o no autorizado para descargar esta partitura.', 'error')
            return redirect(url_for('main.list_digitalized_sheets'))
    except Exception as e:
        current_app.logger.error(f"Error al descargar la partitura: {str(e)}")
        flash(f'Error al descargar la partitura: {str(e)}', 'error')

    return redirect(url_for('main.list_digitalized_sheets'))

# Ruta para digitalizar una partitura
# Requiere haber iniciado sesión
@main.route('/digitalize_and_view/<path:filename>', methods=['GET'])
@login_required
def digitalize_and_view(filename):
    print(f"Comenzando la digitalización de: {filename}")
    original_extension = filename.split('.')[-1]
    user_folder = f'partituras/user_{current_user.get_id()}/'

    if original_extension in ['pdf', 'png', 'jpg', 'jpeg']:
        file_type_folder = original_extension + '/'
    else:
        file_type_folder = 'others/'

    full_blob_name = f"{user_folder}{file_type_folder}{filename}"
    print(f"Ruta completa del archivo en el bucket: {full_blob_name}")

    firestore_db = current_app.config['firestore_db']
    sheet_ref = firestore_db.collection('sheet_music').where('file_path', '==', full_blob_name).get()
    sheet_owned = any(s.to_dict()['username'] == current_user.get_id() for s in sheet_ref)

    if not sheet_owned:
        flash('No autorizado para digitalizar esta partitura.', 'error')
        return redirect(url_for('main.list_sheet_music'))

    input_file_path = download_sheets(current_app.config['FIREBASE_BUCKET_NAME'], filename)
    if input_file_path is None:
        flash('No se pudo descargar el archivo para la digitalización.', 'error')
        return redirect(url_for('main.list_sheet_music'))

    title = filename.rsplit('.', 1)[0]
    sheet_music = SheetMusic(title=title, file_path=input_file_path)
    output_file_path, output_dir = digitalize_sheets(input_file_path, sheet_music)

    if output_file_path:
        mxl_filename = secure_filename(sheet_music.title + '.mxl')
        mxl_full_path = f'{user_folder}mxl/{mxl_filename}'
        blob = current_app.config['firebase_storage'].blob(mxl_full_path)
        blob.upload_from_filename(output_file_path, content_type='application/vnd.recordare.musicxml+xml')

        firestore_db.collection('digitalized_sheets').document(mxl_filename).set({
            'title': title,
            'file_path': mxl_full_path,
            'upload_date': datetime.now(),
            'username': current_user.get_id()
        })

        clean_directory(output_dir)
        flash('Partitura digitalizada correctamente.')
        return redirect(url_for('main.list_digitalized_sheets'))
    else:
        flash('No se pudo digitalizar la partitura.', 'error')
        return redirect(url_for('main.list_sheet_music'))

# Borrado de todos los archivos del directorio pasado por parametro
def clean_directory(directory_path):
    try:
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        current_app.logger.info("Directorio limpiado completamente")
    except Exception as e:
        current_app.logger.error(f"No se pudo limpiar el directorio. Error: {str(e)}")

# Ruta para listar las partituras
# Requiere haber iniciado sesión
# Lista las partituras de formatos que no sean MusicXML accediendo al bucket de Firebase a traves de rutas y a los registros de Firestore
@main.route('/list_sheet_music', methods=['GET'])
@login_required
def list_sheet_music():
    try:
        firestore_db = current_app.config['firestore_db']
        user_id = current_user.get_id()
        sheet_music_files = []

        print(f"Obteniendo partituras para el usuario {user_id}")

        sheets = firestore_db.collection('sheet_music').where('username', '==', user_id).stream()

        for sheet in sheets:
            sheet_data = sheet.to_dict()
            file_name = sheet_data['file_path'].split('/')[-1]
            download_url = url_for('main.digitalize_and_view', filename=file_name)
            doc_id = sheet.id
            
            sheet_music_files.append({
                'name': file_name,
                'url': download_url,
                'doc_id': doc_id
            })

        print(f"Total de partituras listadas: {len(sheet_music_files)}")

    except Exception as e:
        current_app.logger.error(f"Error al listar las partituras: {str(e)}")
        flash(f"Error al listar las partituras: {str(e)}", 'error')
        print(f"Error al listar las partituras: {e}")

    return render_template('list_sheet_music.html', sheet_music_files=sheet_music_files)

# Ruta para visualizar una partitura
# Requiere haber iniciado sesión
# Visualización de una partitura digitalizada
@main.route('/view_sheet/<filename>', methods=['GET'])
@login_required
def view_sheet(filename):
    # Obtiene información del usuario y la partitura
    user_folder = f'partituras/user_{current_user.get_id()}/mxl/'
    full_blob_name = f"{user_folder}{filename}"
    firestore_db = current_app.config['firestore_db']
    sheet_ref = firestore_db.collection('digitalized_sheets').document(filename)
    sheet_doc = sheet_ref.get()

    # Verificación de la existencia de la partitura y si el usuario actual es el propietario
    if not sheet_doc.exists or sheet_doc.to_dict()['username'] != current_user.get_id():
        flash('No autorizado para ver esta partitura.', 'error')
        return redirect(url_for('main.list_digitalized_sheets'))

    try:
        # Verificación del estado de Firebase
        if not firebase_admin._apps:
            cred_dict = json.loads(base64.b64decode(current_app.config['FIREBASE_CREDENTIALS_JSON_BASE64']).decode('utf-8'))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            cred = firebase_admin.get_app().credential.get_credential()

        storage_client = storage.Client(credentials=cred, project=cred.project_id)
        bucket = storage_client.bucket(current_app.config['FIREBASE_BUCKET_NAME'])
        blob = bucket.blob(full_blob_name)

        # Verificación la existencia del archivo
        if not blob.exists():
            current_app.logger.error(f"Archivo no encontrado: {full_blob_name}")
            flash('El archivo solicitado no existe en el almacenamiento.', 'error')
            return redirect(url_for('main.list_digitalized_sheets'))

        # Descarga del contenido del archivo como bytes
        mxl_bytes = blob.download_as_bytes()

        # Archivo MXL como un archivo ZIP
        with zipfile.ZipFile(io.BytesIO(mxl_bytes)) as z:
            for file in z.namelist():
                if file.endswith('.xml'):
                    with z.open(file) as xml_file:
                        xml_content = xml_file.read()
                        break
            else:
                # Si no se encuentra un archivo XML
                flash('El archivo MXL no contiene un archivo XML válido.', 'error')
                return redirect(url_for('main.list_digitalized_sheets'))

        xml_content_b64 = base64.b64encode(xml_content).decode('utf-8')
        return render_template('view_sheet.html', mxl_content=xml_content_b64)

    except zipfile.BadZipFile:
        flash('El archivo MXL no se puede abrir, puede estar corrupto.', 'error')
        return redirect(url_for('main.list_digitalized_sheets'))
    except Exception as e:
        current_app.logger.error(f"Error al descargar la partitura digitalizada: {str(e)}")
        flash(f'Error al descargar la partitura digitalizada: {str(e)}', 'error')
        return redirect(url_for('main.list_digitalized_sheets'))

# Ruta para listar las partituras
# Requiere haber iniciado sesión
# Lista las partituras de formato MusicXML accediendo al bucket de Firebase a traves de rutas y a los registros de Firestore
@main.route('/list_digitalized_sheets', methods=['GET'])
@login_required
def list_digitalized_sheets():
    try:
        firestore_db = current_app.config['firestore_db']
        user_id = current_user.get_id()
        sheet_music_files = []

        sheets = firestore_db.collection('digitalized_sheets').where('username', '==', user_id).stream()

        for sheet in sheets:
            sheet_data = sheet.to_dict()
            full_blob_name = f"partituras/user_{user_id}/mxl/{sheet_data['file_path'].split('/')[-1]}"

            blob = current_app.config['firebase_storage'].blob(full_blob_name)
            if blob.exists():
                download_url = url_for('main.view_sheet', filename=sheet_data['file_path'].split('/')[-1])
                sheet_music_files.append({
                    'name': sheet_data['file_path'].split('/')[-1],
                    'url': download_url,
                    'doc_id': sheet.id
                })
            else:
                current_app.logger.error(f"Archivo no encontrado en Firebase Storage: {full_blob_name}")
                sheet.ref.delete()

        return render_template('list_digitalized_sheets.html', sheet_music_files=sheet_music_files)

    except Exception as e:
        current_app.logger.error(f"Error al listar las partituras digitalizadas: {str(e)}")
        flash(f"Error al listar las partituras digitalizadas: {str(e)}", 'error')
        return redirect(url_for('main.home'))

# Función para preprocesar imágenes
def preprocess_image(file_path, median_kernel_size, adaptive_threshold_block_size, adaptive_threshold_c, erosion_iterations, dilation_iterations):
    # Manejo de las imágenes y pdfs
    try:
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            if not images:
                raise FileNotFoundError("No se pudieron convertir las páginas del PDF a imágenes.")
            image = images[0]
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        else:
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"No se pudo cargar la imagen desde la ruta: {file_path}")
        
        # Aplicación del filtro de Mediana y Umbral Adaptativo
        img = cv2.medianBlur(img, median_kernel_size)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, adaptive_threshold_block_size, adaptive_threshold_c)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Aplicación erosión y dilatación
        img = cv2.erode(img, kernel, iterations=erosion_iterations)
        img = cv2.dilate(img, kernel, iterations=dilation_iterations)
        
        processed_file_path = file_path.replace(".png", "_processed.png").replace(".pdf", "_processed.png").replace(".jpg", "_processed.jpg").replace(".jpeg", "_processed.jpeg")
        cv2.imwrite(processed_file_path, img)
        return processed_file_path
    except Exception as e:
        raise e

# Ruta para listar las partituras registradas
# Requiere haber iniciado sesión
# Obtiene los parámetros de preprocesamiento y preprocesa la imagen
@main.route('/preprocess/<path:filename>', methods=['GET', 'POST'])
@login_required
def preprocess(filename):
    user_folder = f'user_{current_user.get_id()}'
    file_extension = filename.split('.')[-1]
    full_blob_name = f'partituras/{user_folder}/{file_extension}/{filename}'
    
    firestore_db = current_app.config['firestore_db']
    sheet_ref = firestore_db.collection('sheet_music').where('file_path', '==', full_blob_name).where('username', '==', current_user.get_id()).stream()
    
    if not any(sheet_ref):
        flash('No autorizado para procesar esta partitura.', 'error')
        return redirect(url_for('main.list_sheet_music'))

    if request.method == 'POST':
        try:
            # Validaciones y obtención de los parámetros
            median_kernel_size = int(request.form.get('median_kernel_size', 5))
            if median_kernel_size > 15:
                flash('El tamaño máximo permitido para el Kernel Mediano es 15.', 'error')
                return redirect(url_for('main.preprocess', filename=filename))

            adaptive_threshold_block_size = int(request.form.get('adaptive_threshold_block_size', 11))
            if adaptive_threshold_block_size > 31:
                flash('El tamaño máximo permitido para el Bloque de Umbral Adaptativo es 31.', 'error')
                return redirect(url_for('main.preprocess', filename=filename))

            adaptive_threshold_c = int(request.form.get('adaptive_threshold_c', 2))
            if adaptive_threshold_c < 0 or adaptive_threshold_c > 10:
                flash('El valor para C debe estar entre 0 y 10.', 'error')
                return redirect(url_for('main.preprocess', filename=filename))

            erosion_iterations = int(request.form.get('e_iterations', 1))
            if erosion_iterations > 5:
                flash('El número máximo de iteraciones de erosión es 5.', 'error')
                return redirect(url_for('main.preprocess', filename=filename))

            dilation_iterations = int(request.form.get('d_iterations', 1))
            if dilation_iterations > 5:
                flash('El número máximo de iteraciones de dilatación es 5.', 'error')
                return redirect(url_for('main.preprocess', filename=filename))

            # Descarga del archivo de Firebase Storage
            input_file_path = download_sheets(current_app.config['FIREBASE_BUCKET_NAME'], filename)
            if input_file_path is None:
                flash('No se pudo descargar el archivo para el preprocesamiento.', 'error')
                return redirect(url_for('main.list_sheet_music'))

            # Procesamiento de la imagen
            processed_file_path = preprocess_image(input_file_path, median_kernel_size, adaptive_threshold_block_size, adaptive_threshold_c, erosion_iterations, dilation_iterations)
            if processed_file_path:
                # Descarga del archivo
                return send_file(processed_file_path, as_attachment=True)
            else:
                flash('No se pudo procesar la imagen.', 'error')
                return redirect(url_for('main.list_sheet_music'))
                
        except Exception as e:
            flash(f'Error al procesar la imagen: {e}', 'error')
            return redirect(url_for('main.preprocess', filename=filename))

    # Carga inicial de la página de formulario o manejo de otros métodos GET
    else:
        return render_template('preprocess_form_page.html', filename=filename)

def configure_routes(app):
    app.register_blueprint(main)
