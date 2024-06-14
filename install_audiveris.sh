#!/bin/bash

mkdir -p /app/audiveris/bin
mkdir -p /app/audiveris/lib

curl -L -o /app/audiveris/audiveris.zip https://github.com/Audiveris/audiveris/archive/refs/tags/5.3.1.zip

if [ ! -f /app/audiveris/audiveris.zip ]; then
  echo "Error: No se pudo descargar el archivo ZIP de Audiveris."
  exit 1
fi

unzip /app/audiveris/audiveris.zip -d /app/audiveris/

if [ ! -d /app/audiveris/audiveris-5.3.1 ]; then
  echo "Error: No se pudo descomprimir el archivo ZIP de Audiveris."
  exit 1
fi

mv /app/audiveris/audiveris-5.3.1/bin/* /app/audiveris/bin/
mv /app/audiveris/audiveris-5.3.1/lib/* /app/audiveris/lib/

cp /app/DigitalizacionPartiturasApp/audiveris/bin/run_audiveris.sh /app/audiveris/bin/

chmod +x /app/audiveris/bin/run_audiveris.sh
