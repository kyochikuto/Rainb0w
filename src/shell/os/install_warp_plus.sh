#!/bin/bash

source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/base/config.sh
source $PWD/src/shell/os/os_utils.sh

BINARY_PATH="$HOME/warp-plus"

if [ ! -f "$BINARY_PATH" ]; then
    echo -e "${B_GREEN}>> Downloading WARP Plus ${RESET}"
    curl -fsSL -o $HOME/warp-plus_linux-amd64.zip https://github.com/bepass-org/warp-plus/releases/latest/download/warp-plus_linux-amd64.zip

    unzip -o $HOME/warp-plus_linux-amd64.zip -d $HOME
    chmod +x $HOME/warp-plus


    # Start the process in the background, redirecting output through tee for capture
    echo -e "${B_GREEN}>> Registering the device on Cloudflare WARP ${RESET}"
    $BINARY_PATH | tee >(while read -r line; do
        if [[ "$line" == *'level=INFO msg="successfully loaded warp identity" subsystem=warp/account'* ]]; then
            echo -e "${B_GREEN}<< Cloudflare WARP private key registered successfully! >>${RESET}"
            # Find the process ID and kill it
            pkill -f "$BINARY_PATH"
            exit 0
        fi
    done)
fi