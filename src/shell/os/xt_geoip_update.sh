#!/bin/bash

if [ "$(lsmod | grep ^xt_geoip)" ]; then
    curl -fsSL "https://github.com/kyochikuto/sing-box-geodata/releases/latest/download/agg_cidrs.csv" >/tmp/agg_cidrs.csv

    # Check if it is newer than what we already have
    if cmp -s /usr/libexec/rainb0w/agg_cidrs.csv /tmp/agg_cidrs.csv; then
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
fi
