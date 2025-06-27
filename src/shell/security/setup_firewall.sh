#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/os/os_utils.sh

INTERFACE=$(ip route get 8.8.8.8 | awk '{print $5}')

function fn_increase_connctrack_limit() {
    local MEM=$(free | awk '/^Mem:/{print $2}' | awk '{print $1*1000}')
    local CONNTRACK_MAX=$(awk "BEGIN {print $MEM / 16384 / 2}")
    local CONNTRACK_MAX=$(bc <<<"scale=0; $CONNTRACK_MAX/1")
    if [ "$(sysctl -n net.netfilter.nf_conntrack_max)" -ne "$CONNTRACK_MAX" ]; then
        if [ ! -d "/etc/sysctl.d" ]; then
            mkdir -p /etc/sysctl.d
        fi
        if [ ! -f "/etc/sysctl.d/99-x-firewall.conf" ]; then
            echo -e "${GREEN}>> Increasing Connection State Tracking Limits ${RESET}"
            touch /etc/sysctl.d/99-x-firewall.conf
            echo "net.netfilter.nf_conntrack_max=$CONNTRACK_MAX" | tee -a /etc/sysctl.d/99-x-firewall.conf >/dev/null
            sysctl -p /etc/sysctl.d/99-x-firewall.conf >/dev/null
        fi
    fi
}

# Increase resource limits
fn_increase_connctrack_limit

# Resetting policies to avoid getting locked out until changes are saved!
iptables -P INPUT ACCEPT
ip6tables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
ip6tables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
ip6tables -P OUTPUT ACCEPT

echo -e "${B_GREEN}>> Flushing iptables rules to begin with a clean slate${RESET}"
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Restart Docker service to re-insert its rules
echo -e "${B_GREEN}>> Setting up Docker network ${RESET}"
systemctl restart docker
sleep 1

echo -e "${B_GREEN}>> Allow already established connections by other rules${RESET}"
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT
ip6tables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT

echo -e "${B_GREEN}>> Allow local loopback connections ${RESET}"
iptables -A INPUT -i lo -m comment --comment "Allow loopback connections - Rainb0w" -j ACCEPT
ip6tables -A INPUT -i lo -m comment --comment "Allow loopback connections - Rainb0w" -j ACCEPT
iptables -A INPUT ! -i lo -s 127.0.0.0/8 -j REJECT
ip6tables -A INPUT ! -i lo -s ::1/128 -j REJECT
iptables -A OUTPUT -o lo -m comment --comment "Allow loopback connections - Rainb0w" -j ACCEPT
ip6tables -A OUTPUT -o lo -m comment --comment "Allow loopback connections - Rainb0w" -j ACCEPT

echo -e "${B_GREEN}>> Allow ping ${RESET}"
iptables -A INPUT -p icmp --icmp-type 8 -m conntrack --ctstate NEW -m comment --comment "Allow ping" -j ACCEPT
ip6tables -A INPUT -p icmpv6 -m comment --comment "Allow ping" -j ACCEPT

echo -e "${B_GREEN}>> Allow SSH ${RESET}"
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m comment --comment "Allow SSH" -j ACCEPT
ip6tables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m comment --comment "Allow SSH" -j ACCEPT

echo -e "${B_GREEN}>> Drop ALL incoming connections except from Iran and Cloudflare ${RESET}"
# Log any connection attempts not originating from Iran or Cloudflare
#  to '/var/log/kern.log' tagged with the prefix below
iptables -A INPUT -m geoip ! --src-cc IR,CF -m limit --limit 5/min -j LOG --log-prefix '** SUSPECT ** '
ip6tables -A INPUT -m geoip ! --src-cc IR,CF -m limit --limit 5/min -j LOG --log-prefix '** SUSPECT ** '
# Log any connection attempts originating from Iran
#  to '/var/log/kern.log' tagged with the prefix below
iptables -A INPUT -m geoip --src-cc IR -m limit --limit 5/min -j LOG --log-prefix '** IRAN ** '
ip6tables -A INPUT -m geoip --src-cc IR -m limit --limit 5/min -j LOG --log-prefix '** IRAN ** '
iptables -A INPUT -m geoip --src-cc IR,CF -m comment --comment "Drop everything except Iran and Cloudflare" -j ACCEPT
ip6tables -A INPUT -m geoip --src-cc IR,CF -m comment --comment "Drop everything except Iran and Cloudflare" -j ACCEPT
iptables -I FORWARD -i $INTERFACE -m geoip ! --src-cc IR,CF -m conntrack --ctstate NEW -m comment --comment "Drop everything except Iran and Cloudflare" -j DROP
ip6tables -I FORWARD -i $INTERFACE -m geoip ! --src-cc IR,CF -m conntrack --ctstate NEW -m comment --comment "Drop everything except Iran and Cloudflare" -j DROP

echo -e "${B_GREEN}>> Allow HTTP and HTTPS/QUIC ${RESET}"
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -m comment --comment "Allow HTTP" -j ACCEPT
ip6tables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -m comment --comment "Allow HTTP" -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow HTTPS" -j ACCEPT
ip6tables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow HTTPS" -j ACCEPT
iptables -A INPUT -p udp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow QUIC" -j ACCEPT
ip6tables -A INPUT -p udp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow QUIC" -j ACCEPT

echo -e "${B_GREEN}>> Allow Hysteria UDP ${RESET}"
iptables -A INPUT -p udp --dport 8443 -m conntrack --ctstate NEW -m comment --comment "Allow Hysteria" -j ACCEPT
ip6tables -A INPUT -p udp --dport 8443 -m conntrack --ctstate NEW -m comment --comment "Allow Hysteria" -j ACCEPT

echo -e "${B_GREEN}>> Drop invalid packets ${RESET}"
iptables -A INPUT -m conntrack --ctstate INVALID -m comment --comment "Drop Invalid Packets" -j DROP
ip6tables -A INPUT -m conntrack --ctstate INVALID -m comment --comment "Drop Invalid Packets" -j DROP

echo -e "${B_GREEN}>> Setting chain's default policies${RESET}"
iptables -P INPUT DROP
ip6tables -P INPUT DROP
iptables -P FORWARD ACCEPT
ip6tables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
ip6tables -P OUTPUT ACCEPT

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
