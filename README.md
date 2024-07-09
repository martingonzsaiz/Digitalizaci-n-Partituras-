![image](https://github.com/martingonzsaiz/Digitalizacion-Partituras/assets/160163628/8229f62d-bd1e-411e-a0e8-75b306794e2e)


# Digitalizacion-Partituras
Este proyecto consiste en el desarrollo de una aplicación web que permite el almacenamiento, gestión, preprocesamiento y digitalización de partituras musicales, facilitando su acceso y preservación. Utiliza una herramienta de reconocimiento óptico de música llamada Audiveris para transcribir partituras a formato MusicXML, además de otras para la gestión y visualización de las partituras.

## Descripción del Proyecto

La preservación y acceso al contenido musical antiguo, es crucial garantizar que las futuras generaciones puedan trabajar y estudiar estas obras. Por ello la transcripción de partituras mediante su digitalización es esencial para evitar su deterioro y pérdida, además facilita su acceso mediante plataformas digitales.

Este proyecto busca proporcionar una plataforma web accesible y fácil de usar que permita la digitalización, almacenamiento y gestión de partituras musicales.

## Características

- **Autenticación segura**: Gestión de usuarios con autenticación encriptada.
- **Almacenamiento de partituras**: Servicio online para subir y borrar partituras haciendo uso de Firebase.
- **Digitalización de partituras**: Uso de Audiveris para transcribir partituras a MusicXML.
- **Preprocesamiento manual**: Mejoras en la calidad de la imagen de la partitura con funciones de procesamiento de imágenes.
- **Visualización de partituras**: Uso de la librería Verovio para visualizar partituras digitalizadas.
- **Obtención de metadatos**: Automatización en la obtención de metadatos de partituras.

## Uso rápido con Docker
Para probar la aplicación de manera rápida es posible usar la imagen Docker subida en Docker Hub. 
1. Primero es necesario descargar la imagen:
docker pull martingonzsaiz/melodymatrix:latest
2. Luego es necesario configurar las variables de entorno. Se puede ejecutar la imagen pasando las credenciales como parametros del comando.
docker run -p 5000:5000 -e PORT=5000 -e FIREBASE_CREDENTIALS_JSON_BASE64=<credencial_firebase_codificada> -e FIREBASE_BUCKET_NAME=<nombre_bucket> martingonzsaiz/melodymatrix:latest
3. Finalmente se podría iniciar el contenedor.
http://localhost:5000 

## Instalación y preparación del entorno
En primer lugar, sería necesario clonar el repositorio. Para ello hay que realizar el comando siguiente en la terminal CMD o en el PowerShell:
git clone https://github.com/martingonzsaiz/Digitalizacion-Partituras.git
Luego sería necesario moverse al directorio en cuestión para seguir con las siguientes instrucciones.
cd Digitalizacion-Partituras seguido de cd DigitalizaciónPartiturasApp

Después se creó un entorno virtual en el que se trabajó y se llevó el desarrollo. La creación del entorno virtual se alcanza con los siguientes comandos:
python -m venv entorno_partituras 
entorno_partitiuras\Scripts\activate
De esta manera se facilita el manejo del entorno y se asegura el aislamiento de las dependencias y su mayor gestión. Así las dependencias de este proyecto no entran en conflicto con dependencias externas. Si el entorno está activado aparece su nombre al principio de la línea de comandos.

Tras esto, es necesario instalar las dependencias del proyecto, para llevarlo a cabo se utiliza el comnado:
pip install -r requirements.txt

A continuación, es necesario tener claros ciertos aspectos de la aplicación. En esta aplicación se utilizan valores de variables para preparar el entorno de manera segura y efectiva. Estos valores son FIREBASE_CREDENTIALS_JSON_BASE64 y FIREBASE_BUCKET_NAME.
Las credenciales de Firebase sirven para que la aplicación se autentique y pueda acceder a los servicios de Firebase. En el caso de esta aplicación se hace uso de Firestore y Firebase Storage, por ello es necesario generar estas claves y definirlas como variables. Para ello habría que seguir unos pasos extra:

## En Firebase Storage:
1.	Ir a Firebase Console.
2.	Crear o seleccionar el proyecto.
3.	Ir a Configuración del proyecto > Cuentas de servicio.
4.	Seleccionar “Generar nueva clave privada” y guardar el archivo JSON generado.
5.	Se podría codificar las credenciales con el siguiente comando: certutil -encode input.json output.txt 

## En Firebase Bucket:
1.	Acceder a Firebase Console y entrar en el proyecto.
2.	Entrar en Storage.
3.	Copiar el nombre del bucket.

Ahora es necesario configurar las variables de entorno para poder cargar y preparar las credenciales desde el entorno del sistema haciendo uso de la biblioteca os, tal y como se hace en el archivo config.py.
1.	Ir a Sistema>Configuración avanzada del sistema>Variables de Entorno
2.	En Variables del sistema, es necesario crear las nuevas variables de entorno: FIREBASE_CREDENTIALS_JSON_BASE64, FIREBASE_BUCKET_NAME.
3.	Aplicar los cambios
Con esta configuración se podría reutilizar el archivo config.py del repositorio.

Tras asegurarse de que el entorno virtual esta ejecutado, se podría ejecutar la aplicación con el comando:
python run.py
Y acceder a ella a través del navegador con http://127.0.0.1:5000, pudiendo interactuar con todas las funcionalidades de la aplicación localmente.

## Construcción del Docker
Para la construcción del Docker habría que revisar y actualizar todas las nuevas dependencias que tiene la aplicación tras un desarrollo de una nueva funcionalidad para la aplicación. Todas estas nuevas dependencias se deberían añadir en la sección del Docker referente al RUN:
"RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libtesseract-dev \
    tesseract-ocr \
    libfreetype6-dev \
    ghostscript \
    imagemagick \
    openjdk-17-jdk \
    dos2unix \
    poppler-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*"
Tambien sería necesario añadir todas las nuevas variables de entorno que se requieran y realizar cambios en la imagen si se han añadido archivos o se han modificado antiguos.
Finalmente, se podría construir el Docker y subir la imagen. Para ello hay que usar el siguiente comando:
docker build -t melodymatrix .

## Despliegue en Heroku
La configuración de los archivos y servicios para el despliegue de la aplicación se llevó a cabo para el despliegue de la aplicación con Heroku. Sin embargo, a pesar de que la aplicación está desplegada, no es posible realizar todas las funcionalidades de la aplicación debido a un exceso de memoria dentro del plan gratuito de este servicio.
Debido a esto dentro de la aplicación desplegada no es posible digitalizar las partituras ya que este proceso excede la memoria. No obstante, se va a explicar el despliegue para llegar a este futuro desarrollo si cabe.
Tras la construcción del Docker, sería necesario iniciar sesión en Heroku CLI y en el registro de contenedores mediante los comandos: 
heroku login. 
heroku container:login 
Luego sería necesario crear una aplicación en Heroku, construir la imagen y publicarla en Heroku:
heroku create melodymatrix
heroku container:push web -a melodymatrix

Finalmente se podría lanzar el contenedor a heroku para después abrir la aplicación públicamente, dando acceso a cualquier usuario con el enlace de esta:
heroku container:release web -a melodymatrix
heroku open -a melodymatrix
En caso de que haya cualquier fallo o si se quiere revisar el flujo de la aplicación se puede usar el siguiente comando para visualizar los logs:
heroku logs --tail -a melodymatrix

## Tecnologías Utilizadas
- **Backend**: Flask, Python
- **Frontend**: Bootstrap y CSS
- **Almacenamiento**: Firebase
- **OMR**: Audiveris
- **Contenedores**: Docker
- **Despliegue**: Heroku
- **Control de Versiones**: GitHub
- **Gestión del proyecto**: Trello
