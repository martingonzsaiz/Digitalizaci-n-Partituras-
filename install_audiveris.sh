#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt install -y openjdk-11-jdk git unzip

git clone https://github.com/Audiveris/audiveris.git /app/audiveris/audiveris_repo
cd /app/audiveris/audiveris_repo

git checkout development
git pull --all

./gradlew build

echo "Contenido de /app/audiveris:"
ls -l /app/audiveris
echo "Contenido de /app/audiveris/audiveris_repo:"
ls -l /app/audiveris/audiveris_repo
echo "Contenido de /app/audiveris/audiveris_repo/build/distributions:"
ls -l /app/audiveris/audiveris_repo/build/distributions

unzip /app/audiveris/audiveris_repo/build/distributions/Audiveris.zip -d /app/audiveris/

echo "Contenido de /app/audiveris después de extraer:"
ls -l /app/audiveris

mv /app/audiveris/Audiveris/bin/* /app/audiveris/bin/
mv /app/audiveris/Audiveris/lib/* /app/audiveris/lib/
cp /app/DigitalizacionPartiturasApp/audiveris/bin/run_audiveris.sh /app/audiveris/bin/
chmod +x /app/audiveris/bin/run_audiveris.sh

echo "Contenido final de /app/audiveris/bin:"
ls -l /app/audiveris/bin
