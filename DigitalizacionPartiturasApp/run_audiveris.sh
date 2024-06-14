#!/bin/bash

OUTPUT_DIR="/app/audiveris/output"
INPUT_FILE="$1"
JAVA_EXE="/usr/bin/java"
CLASSPATH="/app/audiveris/lib/*"

if [ ! -f "$INPUT_FILE" ]; then
  echo "El archivo $INPUT_FILE no existe"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

$JAVA_EXE -cp $CLASSPATH Audiveris -batch -export -output "$OUTPUT_DIR" -- "$INPUT_FILE"
