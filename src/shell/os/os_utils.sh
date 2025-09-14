#!/bin/bash
source $PWD/src/shell/base/colors.sh

function fn_check_for_pkg() {
    if [ $(dpkg-query -W -f='${Status}' $1 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
        echo false
    else
        echo true
    fi
}

function fn_check_and_install_pkg() {
    local IS_INSTALLED=$(fn_check_for_pkg $1)
    if [ $IS_INSTALLED = false ]; then
        echo -e "${B_GREEN}>> Installing '$1'... ${RESET}"
        apt install -y $1
    fi
}

function fn_install_required_packages() {
    echo -e "${B_GREEN}>> Checking for and installing requried packages${RESET}"
    source $PWD/src/shell/os/upgrade_os.sh
    fn_check_and_install_pkg net-tools
    fn_check_and_install_pkg build-essential
    fn_check_and_install_pkg autoconf
    fn_check_and_install_pkg pkg-config
    fn_check_and_install_pkg dkms
    fn_check_and_install_pkg curl
    fn_check_and_install_pkg unzip
    fn_check_and_install_pkg openssl
    fn_check_and_install_pkg bc
    fn_check_and_install_pkg logrotate
    fn_check_and_install_pkg iptables-persistent
    fn_check_and_install_pkg python3-pip
    fn_check_and_install_pkg python3-venv
    fn_check_and_install_pkg snapd
    fn_check_and_install_pkg apache2-utils
}

function fn_activate_venv() {
    if [ ! -d "$HOME/Rainb0w/.venv" ]; then
        echo -e "${B_GREEN}>> Creating a new Python virtual environment${RESET}"
        python3 -m venv .venv
        source .venv/bin/activate
        pip3 install --upgrade --prefer-binary --requirement $PWD/requirements.txt
    else
        echo -e "${B_GREEN}>> Activating the Python virtual environment${RESET}"
        source .venv/bin/activate    
    fi
}
