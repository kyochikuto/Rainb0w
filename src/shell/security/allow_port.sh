#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/os/os_utils.sh

# $1 -> Proxy title
# $2 -> Port number
# $3 -> Protocol type

echo -e "${B_GREEN}>> Allow $1 Port $2/$3 ${RESET}"
# Grab the line number of the rule that has the comment 'Drop Invalid Packets'
LINENUM=$(iptables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')
# Insert the rule above the $LINENUM we got above
iptables -I INPUT $LINENUM -p $3 --dport $2 -m conntrack --ctstate NEW -m comment --comment "Allow $1" -j ACCEPT
ip6tables -I INPUT $LINENUM -p $3 --dport $2 -m conntrack --ctstate NEW -m comment --comment "Allow $1" -j ACCEPT

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
