#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/os/os_utils.sh

# $1 -> Domain


echo -e "${B_GREEN}>> Getting TLS certs for '$1' and '*.$1' ${RESET}"
certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/certbot/cloudflare.ini \
  -d "$1" -d "*.$1" \
  --non-interactive \
  --agree-tos
