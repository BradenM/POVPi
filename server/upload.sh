#!/usr/bin/env bash

# Upload to RPI

UP_PATH="pi@$RPI:~/povpi/"
ROOT=$(git rev-parse --show-toplevel)
CHANGED=($(git status --porcelain --ignored . | cut -c 4-))
IGNORE=("server/Pipfile.lock" "server/upload.sh")

# Check if in array
contains() {
    [[ "$1" =~ (^|[[:space:]])"$2"($|[[:space:]]) ]];
}


printf "Starting Upload to Pi @ $RPI\n\n"

for i in "${CHANGED[@]}"; do
    file="${ROOT}/${i}"
    if [ -f "${file}" ] && ! contains "$IGNORE" "$i"; then
        printf "Uploading: ${file}\n"
        scp "${file}" "${UP_PATH}${i}"
        printf "\n"
    fi
done


printf "\nUpload Complete.\n"
