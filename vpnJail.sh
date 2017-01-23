#!/bin/bash
if [ $# != 2 ]; then #Check the arguments
    echo "Wrong Arguments Provided"
    echo "1. VPN Config e.g. /home/liam/vpn.ovpn"
    echo "2. Process to Run e.g. Firefox"
    exit 1
fi

if [ ! -d "$1" ]; then #Check to make sure it's a legit file
  echo "The directory/file for the VPN Config doesn't exist. Sorry"
  exit 1
fi

if [ "$EUID" -ne 0 ] #Check if root
  then echo "Please run as root e.g. Sudo ./vpnjail.sh"
  exit
fi



vpn_config="$1" 
process="$2"
vpn_ip=$(grep "^[^#;]" ${vpn_config} | grep remote | cut -d " " -f2)

ip netns del vpn
ip link del vpn0
ip netns add vpn #Create a network namespace
ip netns exec vpn ip addr add 127.0.0.1/8 dev lo #add a loopback device
ip netns exec vpn ip link set lo up #Start up the loopback device that we created

ip link add vpn0 type veth peer name vpn1 #Create a virtual ethernet pair
ip link set vpn0 up #Start one the local side
ip link set vpn1 netns vpn up #pass one side to the namespace
ip addr add 10.200.200.1/24 dev vpn0 #Give the local side an ip
ip netns exec vpn ip addr add 10.200.200.2/24 dev vpn1 #Give the other side an IP
ip netns exec vpn ip route add default via 10.200.200.1 dev vpn1 #Route traffic to the other veth


iptables -A INPUT \! -i vpn0 -s 10.200.200.0/24 -j DROP #Drop packets to an interface that doesn't exist
iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o en+ -j MASQUERADE #Pass stuff to somthing else ?
sysctl -q net.ipv4.ip_forward=1 #Start ipv4 fowarding

mkdir -p /etc/netns/vpn #DNS
echo 'nameserver 8.8.8.8' > /etc/netns/vpn/resolv.conf #DNS (Google)

ip netns exec vpn iptables -A OUTPUT -o tun0 -j ACCEPT #Accept traffic though the vpn interface 
ip netns exec vpn iptables -A OUTPUT -o vpn1 -d  ${vpn_ip} -j ACCEPT #Accept trafic to our vpn provider
ip netns exec vpn iptables -A OUTPUT -o vpn1 -d 10.200.200.1  -j ACCEPT #Allow communication to itself
ip netns exec vpn iptables -A OUTPUT -o vpn1 -d 10.200.200.2  -j ACCEPT #Allow communication to the veth pair
ip netns exec vpn iptables -A OUTPUT -o vpn1 -j DROP #Drop any other traffic




ip netns exec vpn openvpn --config ${vpn_config} & #Start openvpn in the net space
while ! ip netns exec vpn ip a show dev tun0 up; do sleep .5; done #While the interface is not up do nothing
ip netns exec vpn ${process} #Start a command
