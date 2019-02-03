#!/usr/bin/env bash

# Upload to RPI

UP_PATH="pi@$RPI:~/povdisplay"

printf "Starting Upload to Pi @ $RPI\n"
scp *.py .env $UP_PATH
scp -rp ./certs ./device_setup $UP_PATH

printf "Upload Complete.\n"
