#!/bin/bash

mkdir -p /app/audiveris/bin /app/audiveris/lib

git clone https://github.com/Audiveris/audiveris.git /app/audiveris/audiveris_repo

cd /app/audiveris/audiveris_repo

git checkout development
git pull --all

./gradlew build

unzip build/distributions/Audiveris.zip -d /app/audiveris/

mv /app/audiveris/Audiveris/bin/* /app/audiveris/bin/
mv /app/audiveris/Audiveris/lib/* /app/audiveris/lib/

cp /app/DigitalizacionPartiturasApp/audiveris/bin/run_audiveris.sh /app/audiveris/bin/

chmod +x /app/audiveris/bin/run_audiveris.sh
