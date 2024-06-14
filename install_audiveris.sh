#!/bin/bash

check_last_command() {
  if [ $? -ne 0 ]; then
    echo "Error en el paso: $1"
    exit 1
  fi
}

echo "Actualizando y mejorando el sistema..."
sudo apt update
check_last_command "sudo apt update"

sudo apt upgrade -y
check_last_command "sudo apt upgrade"

echo "Instalando dependencias..."
sudo apt install -y git unzip openjdk-17-jdk
check_last_command "sudo apt install"

echo "Clonando el repositorio de Audiveris..."
git clone https://github.com/Audiveris/audiveris.git /app/audiveris/audiveris_repo
check_last_command "git clone"

cd /app/audiveris/audiveris_repo
check_last_command "cd /app/audiveris/audiveris_repo"

echo "Seleccionando la rama de desarrollo..."
git checkout development
check_last_command "git checkout development"

git pull --all
check_last_command "git pull --all"

echo "Configurando JAVA_HOME y PATH..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
echo "JAVA_HOME=$JAVA_HOME"
echo "PATH=$PATH"

echo "Haciendo ejecutable gradlew..."
chmod +x gradlew
check_last_command "chmod +x gradlew"

echo "Compilando el proyecto con Gradle..."
./gradlew build
check_last_command "./gradlew build"

echo "Contenido de /app/audiveris/audiveris_repo/build/distributions:"
ls -l /app/audiveris/audiveris_repo/build/distributions
check_last_command "ls build/distributions"

echo "Extrayendo el archivo distribuido..."
unzip /app/audiveris/audiveris_repo/build/distributions/Audiveris.zip -d /app/audiveris/
check_last_command "unzip Audiveris.zip"

echo "Contenido de /app/audiveris después de extraer:"
ls -l /app/audiveris
check_last_command "ls /app/audiveris"

echo "Creando directorios bin y lib..."
mkdir -p /app/audiveris/bin
check_last_command "mkdir -p /app/audiveris/bin"

mkdir -p /app/audiveris/lib
check_last_command "mkdir -p /app/audiveris/lib"

echo "Moviendo archivos bin y lib..."
mv /app/audiveris/Audiveris/bin/* /app/audiveris/bin/
check_last_command "mv bin/*"

mv /app/audiveris/Audiveris/lib/* /app/audiveris/lib/
check_last_command "mv lib/*"

echo "Copiando y configurando run_audiveris.sh..."
cp /app/DigitalizacionPartiturasApp/audiveris/bin/run_audiveris.sh /app/audiveris/bin/
check_last_command "cp run_audiveris.sh"

chmod +x /app/audiveris/bin/run_audiveris.sh
check_last_command "chmod +x run_audiveris.sh"

echo "Contenido final de /app/audiveris/bin:"
ls -l /app/audiveris/bin
check_last_command "ls final bin"

echo "Instalación y configuración completadas con éxito."
