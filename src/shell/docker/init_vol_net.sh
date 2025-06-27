#!/bin/bash
source $PWD/src/shell/base/colors.sh

if ! docker network list | awk '{print $2}' | grep -q '^web$'; then
    echo -e "${B_GREEN}>> Creating a Docker network for NGINX's front-end ${RESET}"
    docker network create web >/dev/null
fi

if ! docker network list | awk '{print $2}' | grep -q '^proxy-tier$'; then
    echo -e "${B_GREEN}>> Creating a Docker network for proxies ${RESET}"
    docker network create proxy-tier >/dev/null
fi