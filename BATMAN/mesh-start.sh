#!/bin/bash

# Change these for each node as needed
IFACE=${IFACE:-$(iw dev | awk '$1=="Interface"{print $2}' | head -n1)}
MESH_ID=${MESH_ID:-batmesh}
FREQ=${FREQ:-2412}

# Get the MAC address of the interface
MAC=$(cat /sys/class/net/$IFACE/address)

# Extract the last two octets
OCTET1=$(echo $MAC | cut -d: -f5)
OCTET2=$(echo $MAC | cut -d: -f6)

# Convert hex to decimal
IP_SUFFIX1=$((0x$OCTET1))
IP_SUFFIX2=$((0x$OCTET2))

# Generate the IP in your mesh subnet
IP="192.168.199.$IP_SUFFIX1"

echo "[+] Using interface: $IFACE"
echo "[+] MAC address: $MAC"
echo "[+] Assigned IP: $IP"

# Start the mesh
echo "[+] Bringing down $IFACE"
ip link set $IFACE down

echo "[+] Setting IBSS mode on $IFACE"
iw $IFACE set type ibss
ip link set $IFACE up
iw $IFACE ibss join $MESH_ID $FREQ

echo "[+] Attaching $IFACE to batman-adv"
batctl if add $IFACE

echo "[+] Bringing up bat0 and assigning IP"
ip link set up dev bat0
ip addr add $IP/24 dev bat0

echo "[+] BATMAN node is up with IP $IP"
tail -f /dev/null
