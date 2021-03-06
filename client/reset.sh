#!/usr/bin/env bash

# Reset ESP32

# Erase Flash
esptool --port $AMPY_PORT erase_flash

# Reflash
esptool --chip esp32 --port $AMPY_PORT write_flash -z 0x1000 ./esp32.bin

# Upload Files
printf "\n Setting ESP32 Up..."
sleep 5
ampy mkdir /lib
ampy put lib/BlynkLib.py /lib/BlynkLib.py
ampy put timer.py /timer.py
ampy put main.py /main.py
ampy ls
ampy reset

# Load
./update.sh
