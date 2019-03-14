#!/usr/bin/env bash

# Uploads files to ESP

printf "Cleaning Docstrings...\n"
sed "/'''.*'''/d" ./main.py > main_esp.py

printf "Uploading files to ESP...\n"
ampy put main_esp.py /main.py

printf "Cleaning up...:\n"
rm main_esp.py

printf "Upload Complete, connecting...\n"

rshell --port $AMPY_PORT --baud $AMPY_BAUD repl
