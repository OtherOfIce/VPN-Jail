import sys
import subprocess
import shlex
import re
import os.path
import socket


def runCommand(command):
    command = shlex.split(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out = ""
    err = ""
    try:
        out,err = p.communicate(timeout=3)
        if err != b'':
            print(command)
            print(err)
        out = out.decode('ascii').strip()
    except subprocess.TimeoutExpired:
        print("Process Timed out")

    return out

def isRoot():
    return (runCommand("whoami") == "root")




if not isRoot():
    print("Must be running as root")
    exit()


print(sys.argv)
if len(sys.argv) !=  3:
    print("Wrong Arguments Provided")
    print("1. VPN Config e.g. /home/liam/vpn.ovpn")
    print("2. Process to Run e.g. Firefox")
    exit()

vpnFileName = sys.argv[1]
process = sys.argv[2]


if not os.path.isfile(vpnFileName):
    print("Please enter a valid path")
    exit()

vpnFile = open(vpnFileName,'r')

re1 = re.compile(r'^[^#;]')
re2 = re.compile(r"remote")


address = "google.com"
port = "1194"
ip = ""

for line in vpnFile:
    if re.search("remote ",line) != None and  re.search("^[^#;]",line):
        line = line.split()
        address = line[1]
        if len(line) == 3:
            port = line[2]

ip = socket.gethostbyname(address)
print(ip, address,port)


runCommand("ip netns del vpn")
runCommand("ip link del vpn0")
runCommand("ip netns add vpn ") #Create a network namespace
runCommand("ip netns exec vpn ip addr add 127.0.0.1/8 dev lo ") #add a loopback device
runCommand("ip netns exec vpn ip link set lo up ") #Start up the loopback device that we created

runCommand("ip link add vpn0 type veth peer name vpn1 ") #Create a virtual ethernet pair
runCommand("ip link set vpn0 up ") #Start one the local side
runCommand("ip link set vpn1 netns vpn up ") #pass one side to the namespace
runCommand("ip addr add 10.200.200.1/24 dev vpn0 ") #Give the local side an ip
runCommand("ip netns exec vpn ip addr add 10.200.200.2/24 dev vpn1 ") #Give the other side an IP
runCommand("ip netns exec vpn ip route add default via 10.200.200.1 dev vpn1 ") #Route traffic to the other veth

runCommand("iptables -A INPUT \! -i vpn0 -s 10.200.200.0/24 -j DROP") #Drop packets to an interface that doesn't exist
runCommand("iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o en+ -j MASQUERADE ") #Pass stuff to somthing else ?
runCommand("sysctl -q net.ipv4.ip_forward=1 ") #Start ipv4 fowarding

runCommand("mkdir -p /etc/netns/vpn ") #DNS
runCommand("echo 'nameserver 8.8.8.8' > /etc/netns/vpn/resolv.conf ") #DNS (Google)

runCommand("ip netns exec vpn iptables -A OUTPUT -o tun0 -j ACCEPT ") #Accept traffic though the vpn interface 
runCommand("ip netns exec vpn iptables -A OUTPUT -o vpn1 -d  " + ip + " -j ACCEPT ") #Accept trafic to our vpn provider
runCommand("ip netns exec vpn iptables -A OUTPUT -o vpn1 -d 10.200.200.1  -j ACCEPT ") #Allow communication to itself
runCommand("ip netns exec vpn iptables -A OUTPUT -o vpn1 -d 10.200.200.2  -j ACCEPT ") #Allow communication to the veth pair
runCommand("ip netns exec vpn iptables -A OUTPUT -o vpn1 -j DROP ") #Drop any other traffic

runCommand("ip netns exec vpn openvpn --config ./vpn.ovpn & ") #Start openvpn in the net space

runCommand("ip netns exec vpn sudo -u liam " + process) #Start a command