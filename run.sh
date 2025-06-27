#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Allow execution permission
find $PWD -name "*.sh" -exec chmod +x {} \;

source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/base/config.sh
source $PWD/src/shell/os/os_utils.sh

trap '' INT

# OS check
if ! [[ "$DISTRO" =~ "Ubuntu" || "$DISTRO" =~ "Debian" ]]; then
    echo "$DISTRO"
    echo -e "${B_RED}This installer only supports Debian and Ubuntu OS!${RESET}"
    exit 0
else
    # Version check
    if [[ "$DISTRO" =~ "Ubuntu" ]]; then
        case "$DISTRO_VERSION" in
            "20.04"|"22.04"|"24.04") ;;
            *) echo "Your version of Ubuntu is not supported Only 20.04, 22.04, and 24.04 versions are supported."
                exit 0
                ;;
        esac
    elif [[ "$DISTRO" =~ "Debian GNU/Linux" ]]; then
        if [ ! "$DISTRO_VERSION" == "11" ]; then
            echo "Your version of Debian is not supported! Minimum required version is 11"
            exit 0
        else
            # Debian has a quirk that usually comes with an old Kernel without
            # the corresponding headers and modules package available, therefore
            # we need to upgrade to the latest kernel available on the repository first
            apt update
            current_kernel=$(uname -r)
            latest_kernel=$(apt-cache search linux-image | grep -oP '5\.10\.[0-9]+-[0-9]+' | uniq | sort --version-sort | tail -n 1)
            if [[ "$latest_kernel" > "$current_kernel" ]]; then
                fn_check_and_install_pkg linux-image-$latest_kernel-amd64
                fn_check_and_install_pkg linux-headers-$latest_kernel-amd64
                echo -e "${B_GREEN}\n\nA newer kernel '$latest_kernel' is installed on your Debian.${RESET}"
                echo -e "${B_RED}You're server is now going to reboot to load the new kernel and the extra modules required${RESET}"
                echo -e "${B_GREEN}After booting up, run the script again with the following commands to proceed!${RESET}"
                echo -e "${B_YELLOW}cd Rainb0w-Lite"
                echo -e "./run.sh${RESET}"
                systemctl reboot
                exit
            fi
        fi
    fi
fi

# Check for root permissions
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./run.sh)"
    exit
fi

# Install pre-requisites
if [ ! -d "$HOME/Rainb0w_Home" ]; then
    # Install required packages
    fn_install_required_packages
    # Install xtables geoip
    source $PWD/src/shell/os/install_xt_geoip.sh
    # Install Docker
    source $PWD/src/shell/os/install_docker.sh
    # Install Certbot
    source $PWD/src/shell/os/install_certbot.sh
    # Install WARP Plus
    source $PWD/src/shell/os/install_warp_plus.sh
    # Reboot if needed
    source $PWD/src/shell/os/check_reboot_required.sh
    clear
fi

# Setup and activate a Python venv
fn_activate_venv
clear

function clear_and_copy_files() {
    # Cleanup and copy all the template files to let the admin select among them
    rm -rf $HOME/Rainb0w_Home
    mkdir $HOME/Rainb0w_Home
    cp -r ./Docker/* $HOME/Rainb0w_Home/
}

function installer_menu() {
    echo -ne "
Rainb0w Proxy Installer v${VERSION}
[github.com/kyochikuto]

Install: Setup new proxies
Restore: Restore a previous installation's configuration and users

Select installation type:

${GREEN}1)${RESET} Install
${GREEN}2)${RESET} Restore
${RED}0)${RESET} Exit

Choose an option: "
    read -r ans
    case $ans in
    2)
        clear
        python3 $PWD/src/configurator.py "Restore"
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -ne 0 ]; then
            echo "Python configurator did not finish successfully!"
            exit
        fi
        source $PWD/src/shell/deploy.sh "Restore"
        ;;
    1)
        clear
        clear_and_copy_files
        python3 $PWD/src/configurator.py "Install"
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -ne 0 ]; then
            echo "Python configurator did not finish successfully!"
            rm -rf $HOME/Rainb0w_Home
            exit
        fi
        source $PWD/src/shell/deploy.sh "Install"
        ;;
    0)
        exit
        ;;
    *)
        fn_fail
        clear
        installer_menu
        ;;
    esac
}

function main() {
    if [ -d "$HOME/Rainb0w_Home" ]; then
        # We have an existing installation, so let's present the dashboard to change settings
        python3 $PWD/src/dashboard.py
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -eq 1 ]; then
            source $PWD/src/shell/docker/restart_all_containers.sh
            exit
        else
            exit
        fi
    else
        # This is a new installation
        installer_menu
    fi
}

main
