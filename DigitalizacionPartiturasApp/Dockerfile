FROM openjdk:17-jdk-slim-buster

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    git \
    gradle \
    tesseract-ocr \
    libtesseract-dev \
    libfreetype6-dev \
    ghostscript \
    imagemagick \
    python3-pip \
    default-mysql-client \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ajustes de configuración de ImageMagick
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

# Instalar Rust para la compilación de bcrypt
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Instalar Python y librerías necesarias
RUN pip3 install --upgrade pip && \
    pip3 install flask google-cloud-storage flask-login flask_sqlalchemy flask_migrate pymysql bcrypt firebase_admin Pyrebase4

# Copiar archivos y configuración de Google Cloud
COPY ./hip-transducer-422216-m7-5b7489d00ae2.json /app/
COPY . /app

# Clonar y construir Audiveris en el contenedor
RUN if [ -d "/app/audiveris" ]; then rm -rf /app/audiveris; fi && \
    git clone https://github.com/Audiveris/audiveris.git /app/audiveris && \
    cd /app/audiveris && \
    ./gradlew build && \
    ./gradlew run

# Establecer el directorio de trabajo
WORKDIR /app

# Exponer el puerto para Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python3", "run.py"]
