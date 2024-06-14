#!/bin/bash

mkdir -p /app/audiveris/output
mkdir -p /app/audiveris/bin
mkdir -p /app/audiveris/lib

curl -L -o /app/audiveris/audiveris.zip https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.zip
unzip /app/audiveris/audiveris.zip -d /app/audiveris

mv /app/audiveris/Audiveris-5.3.1/bin/* /app/audiveris/bin/
mv /app/audiveris/Audiveris-5.3.1/lib/* /app/audiveris/lib/

chmod +x /app/audiveris/bin/run_audiveris.sh
