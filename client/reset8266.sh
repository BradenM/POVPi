#!/usr/bin/env bash

# Reset ESP

# Erase Flash
esptool --port $AMPY_PORT erase_flash

# Reflash
esptool --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ./esp8266.bin


# Upload Files
printf "\n Setting ESP8266 Up..."
sleep 5
ampy mkdir /lib
ampy put lib/BlynkLib.py /lib/BlynkLib.py
ampy put timer.py /timer.py
ampy put main.py /main.py
ampy ls
ampy reset

# Load
./update.sh
