#!/usr/bin/env bash
source $PWD/src/shell/base/colors.sh

set -euo pipefail

echo -e "${B_GREEN}>> Downloading sing-box binary to generate REALITY security keys${RESET}"
if [ ! -f "/tmp/sing-box/sing-box" ]; then
    curl -L https://github.com/SagerNet/sing-box/releases/download/v1.12.14/sing-box-1.12.14-linux-amd64.tar.gz -o /tmp/sing-box.tar.gz
    tar -xzf /tmp/sing-box.tar.gz -C /tmp/
fi

echo -e "${B_GREEN}>> Generating a x25519 crypto key pair${RESET}"

output=$(/tmp/sing-box-1.12.14-linux-amd64/sing-box generate reality-keypair)

# Extract each key
private_key=$(printf '%s' "$output" | awk -F': *' '/^PrivateKey/ {print $2}')
public_key=$(printf '%s' "$output" | awk -F': *' '/^PublicKey/  {print $2}')

# Save to file
echo "$private_key" > $HOME/.cache/keys.txt
echo "$public_key" >> $HOME/.cache/keys.txt
