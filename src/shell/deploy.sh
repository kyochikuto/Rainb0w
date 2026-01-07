#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/os/os_utils.sh
source $PWD/src/shell/docker/docker_utils.sh

# Create Docker network and shared volumes
source $PWD/src/shell/docker/init_vol_net.sh

# Apply Kernel's network stack optimizations
source $PWD/src/shell/performance/tune_kernel_net.sh

# Activate necessary protections
source $PWD/src/shell/security/setup_firewall.sh

# Get TLS certs
domain=$(python3 $PWD/src/shell/helper/get_domain.py)
source $PWD/src/shell/security/get_tls_certs.sh $domain

if [ ! "$(docker images -q caddy)" ]; then
    docker buildx build --tag caddy $HOME/Rainb0w_Home/caddy/
    if [ ! "$(docker images -q caddy)" ]; then
        echo -e "${B_RED}There was an issue when building a Docker image for 'Caddy', check the logs!${RESET}"
        echo -e "${B_YELLOW}After resolving the issue, run the installer again.${RESET}"
        rm -rf $HOME/Rainb0w_Home
        exit
    fi
fi

fn_restart_docker_container "sing-box"
fn_restart_docker_container "caddy"

echo -e "\n\nYour proxies are ready now!\n"

if [ ! $# -eq 0 ]; then
    if [ "$1" == 'Install' ]; then
        username=$(python3 $PWD/src/shell/helper/get_first_username.py)
        python3 $PWD/src/shell/helper/get_client_url.py $username
    elif [ "$1" == 'Restore' ]; then
        echo -e "User share urls are the same as in your configuration, you can view them in the dashboard"
    else
        echo -e "Invalid mode supplied!"
    fi
fi

echo -e "\nYou can add/remove users or find more options in the dashboard,
in order to display the dashboard run the file 'run.sh' again."
