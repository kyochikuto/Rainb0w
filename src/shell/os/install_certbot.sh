#!/bin/bash

source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/base/config.sh
source $PWD/src/shell/os/os_utils.sh

IS_SNAP_INSTALLED=$(fn_check_for_pkg snapd)
if [ $IS_SNAP_INSTALLED = true ]; then
    echo -e "${B_GREEN}>> Checking for and installing Certbot snap packages ${RESET}"
    snap install --classic certbot
    snap install certbot-dns-cloudflare
    snap set certbot trust-plugin-with-root=ok
    snap install certbot-dns-cloudflare

    mkdir -p ~/.secrets/certbot/
    touch ~/.secrets/certbot/cloudflare.ini
    chmod 600 ~/.secrets/certbot/cloudflare.ini

    mkdir -p /etc/letsencrypt/renewal-hooks/post/
    echo -e '#!/bin/sh\ndocker restart nginx\ndocker restart sing-box' > /etc/letsencrypt/renewal-hooks/post/restart-docker-containers.sh
    chmod +x /etc/letsencrypt/renewal-hooks/post/restart-docker-containers.sh

    echo -e "${B_GREEN}<< Certbot is now installed! >>${RESET}"
fi
