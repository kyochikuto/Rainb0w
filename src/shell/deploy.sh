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

# Setup a fake WordPress blog if we have enough memory
MEMORY_SIZE=$(free -m | awk '/Mem:/ { print $2 }')
if [ $MEMORY_SIZE -gt 512 ]; then
    fn_restart_docker_container "wordpress"
    echo -e "\nWordPress admin area credentials:"
    WP_ADMIN=$(grep -w 'WORDPRESS_ADMIN_USER' $HOME/Rainb0w_Home/wordpress/wp.env | cut -d= -f2)
    WP_ADMIN=${WP_ADMIN//\'/}
    WP_PASSWORD=$(grep -w 'WORDPRESS_ADMIN_PASSWORD' $HOME/Rainb0w_Home/wordpress/wp.env | cut -d= -f2)
    WP_PASSWORD=${WP_PASSWORD//\'/}
    echo -e "WP Admin URL:  ${B_BLUE}https://YOUR_MAIN_DOMAIN/wp-admin ${RESET}"
    echo -e "WP Username:   ${B_GREEN}$WP_ADMIN${RESET}"
    echo -e "WP Password:   ${B_GREEN}$WP_PASSWORD${RESET}"
else
    echo -e "${B_RED}Memory is insufficient to run a WordPress container, consider upgrading your server specs!"
    CONTAINERS=$(echo "$CONTAINERS" | sed 's/wordpress//g')
fi

fn_restart_docker_container "sing-box"
fn_restart_docker_container "nginx"

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
