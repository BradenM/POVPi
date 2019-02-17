#!/usr/bin/env bash

# Uploads files to ESP

printf "Uploading files to ESP...\n"
ampy ls
ampy reset
ampy rm /main.py
ampy rm /timer.py
ampy put main.py /main.py
ampy put timer.py /timer.py
printf "Upload Complete, connecting...\n"

rshell --port $AMPY_PORT --baud $AMPY_BAUD repl
