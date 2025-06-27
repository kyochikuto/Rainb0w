#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/os/os_utils.sh

if [ "$(fn_check_for_pkg xtables-addons-common)" = true ] &&
    [ "$(fn_check_for_pkg libtext-csv-xs-perl)" = true ]; then

    if [ ! -d "/usr/libexec/rainb0w/" ]; then
        mkdir -p /usr/libexec/rainb0w
    fi
    if [ ! -d "/usr/share/xt_geoip" ]; then
        mkdir -p /usr/share/xt_geoip
    fi
    # Copy our builder script if coming from a previous version
    cp $PWD/src/shell/os/xt_geoip_build_agg /usr/libexec/rainb0w/xt_geoip_build_agg
    chmod +x /usr/libexec/rainb0w/xt_geoip_build_agg

    # Get the latest aggregated CIDR database
    echo -e "${B_GREEN}>> Getting the latest aggregated database ${RESET}"
    curl -fsSL "https://github.com/kyochikuto/sing-box-geodata/releases/latest/download/agg_cidrs.csv" >/tmp/agg_cidrs.csv

    # Check if it's the first run
    if [ -f "/usr/libexec/rainb0w/agg_cidr.csv" ]; then
        # Check if it is newer than what we already have
        if cmp -s /usr/libexec/rainb0w/agg_cidr.csv /tmp/agg_cidrs.csv; then
            echo -e "${B_GREEN}Already on the latest database! ${RESET}"
            rm /tmp/agg_cidrs.csv
        else
            mv /tmp/agg_cidrs.csv /usr/libexec/rainb0w/agg_cidrs.csv
            # Convert CSV database to binary format for xt_geoip
            echo -e "${B_GREEN}Newer aggregated CIDR database found, updating now... ${RESET}"
            /usr/libexec/rainb0w/xt_geoip_build_agg -s -i /usr/libexec/rainb0w/agg_cidrs.csv
            # Load xt_geoip kernel module
            modprobe xt_geoip
            lsmod | grep ^xt_geoip
        fi
    else
        mv /tmp/agg_cidrs.csv /usr/libexec/rainb0w/agg_cidrs.csv
        # Convert CSV database to binary format for xt_geoip
        echo -e "${B_GREEN}>> Converting the CIDR database to binary format... ${RESET}"
        /usr/libexec/rainb0w/xt_geoip_build_agg -s -i /usr/libexec/rainb0w/agg_cidrs.csv
        # Load xt_geoip kernel module
        modprobe xt_geoip
        lsmod | grep ^xt_geoip
    fi
else
    fn_install_xt_geoip_module
fi
