#!/bin/bash

AUDIVERIS_VERSION="5.3.1"
AUDIVERIS_URL="https://github.com/Audiveris/audiveris/releases/download/${AUDIVERIS_VERSION}/Audiveris-${AUDIVERIS_VERSION}.zip"
AUDIVERIS_DIR="/app/audiveris"

# Descargar y descomprimir Audiveris
wget $AUDIVERIS_URL -O /tmp/Audiveris.zip
unzip /tmp/Audiveris.zip -d /app
mv /app/Audiveris-${AUDIVERIS_VERSION} $AUDIVERIS_DIR

# Crear el directorio de salida si no existe
mkdir -p $AUDIVERIS_DIR/output

# Hacer que el script de ejecución sea ejecutable
chmod +x $AUDIVERIS_DIR/bin/run_audiveris.sh
