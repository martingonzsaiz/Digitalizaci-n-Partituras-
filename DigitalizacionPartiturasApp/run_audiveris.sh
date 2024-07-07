#!/bin/bash

JAVA_EXE=/usr/bin/java
CLASSPATH="/app/audiveris/build/distributions/Audiveris-5.3.1/lib/*"

echo "Contenido del directorio actual:"
ls -l

echo "Printing environment variables:"
printenv

echo "Inicio del script de digitalización"
OUTPUT_DIR="/app/audiveris_output"
echo "Directorio de salida: $OUTPUT_DIR"

INPUT_FILE="$1"
echo "Archivo de entrada: $INPUT_FILE"

echo "Verificando acceso al archivo de entrada..."
if [ -r "$INPUT_FILE" ]; then
    echo "El archivo de entrada es legible"
else
    echo "El archivo de entrada no es legible"
    ls -l "$INPUT_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
echo "Directorio de salida creado"

echo "Ejecutando Audiveris..."
$JAVA_EXE -cp "$CLASSPATH" org.audiveris.omr.Main -batch -export -output "$OUTPUT_DIR" -- "$INPUT_FILE" &> "${OUTPUT_DIR}/audiveris.log"

exit_status=$?
echo "Audiveris exit status: $exit_status"
exit $exit_status
