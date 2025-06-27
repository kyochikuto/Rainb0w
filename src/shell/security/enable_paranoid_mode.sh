#!/bin/bash
source $PWD/src/shell/base/colors.sh

modprobe xt_geoip
IS_MODULE_LOADED=$(lsmod | grep ^xt_geoip)
if [ ! -z "$IS_MODULE_LOADED" ]; then
    bash $PWD/src/shell/os/install_xt_geoip.sh
fi

if [ -f "$HOME/Rainb0w_Backup/rules.v4" ]; then
    echo -e "${B_GREEN}>> Restoring backed up iptables rules from  $HOME/Rainb0w_Backup/rules.v4 ${RESET}"
    iptables-restore <$HOME/Rainb0w_Backup/rules.v4
    ip6tables-restore <$HOME/Rainb0w_Backup/rules.v6
else
    echo -e "${B_RED}No iptables backup file found at: $HOME/Rainb0w_Backup/rules.v4 ${RESET}"
fi
