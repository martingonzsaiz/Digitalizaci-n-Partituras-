#!/bin/bash

echo "Iniciando instalación de Java..."
apk add --no-cache openjdk17-jdk

echo "Clonando el repositorio de Audiveris..."
git clone https://github.com/Audiveris/audiveris.git /app/audiveris/audiveris_repo

echo "Cambiando a la rama 'development'..."
cd /app/audiveris/audiveris_repo
git checkout development
git pull --all

echo "Compilando Audiveris..."
./gradlew build

echo "Contenido de /app/audiveris/audiveris_repo/build/distributions:"
ls -l /app/audiveris/audiveris_repo/build/distributions

echo "Extrayendo Audiveris..."
unzip /app/audiveris/audiveris_repo/build/distributions/Audiveris.zip -d /app/audiveris

echo "Moviendo archivos bin y lib..."
mv /app/audiveris/Audiveris/bin/* /app/audiveris/bin/
mv /app/audiveris/Audiveris/lib/* /app/audiveris/lib/

echo "Copiando run_audiveris.sh..."
cp /app/DigitalizacionPartiturasApp/audiveris/bin/run_audiveris.sh /app/audiveris/bin/

echo "Asignando permisos de ejecución a run_audiveris.sh..."
chmod +x /app/audiveris/bin/run_audiveris.sh

echo "Contenido final de /app/audiveris/bin:"
ls -l /app/audiveris/bin

echo "Instalación de Audiveris completada."
