#!/bin/bash
#
# Darknet Demo - Module Overview
# Shows all available modules and features
#

echo "====================================="
echo "Darknet Framework - Module Demo"
echo "====================================="
echo ""

# Check if darknet is installed
if ! command -v darknet &> /dev/null; then
    echo "[*] Using local binary..."
    DARKNET="./bin/darknet"
    if [ ! -f "$DARKNET" ]; then
        echo "[!] Please build Darknet first: make"
        exit 1
    fi
else
    DARKNET="darknet"
fi

# Show version
echo "[*] Darknet Version:"
$DARKNET version
echo ""

# Show all modules
echo "[*] Available Modules:"
$DARKNET modules
echo ""

# Show help
echo "[*] Usage Help:"
$DARKNET help
echo ""

echo "====================================="
echo "Quick Command Reference"
echo "====================================="
echo ""
echo "WiFi Module:"
echo "  sudo darknet wifi scan -i wlan0"
echo "  sudo darknet wifi deauth -i wlan0 -b <bssid>"
echo ""
echo "Scan Module:"
echo "  sudo darknet scan ping -r 192.168.1.0/24"
echo "  sudo darknet scan ports -t 192.168.1.1"
echo ""
echo "ARP Module:"
echo "  sudo darknet arp scan -i eth0"
echo "  sudo darknet arp poison -i eth0 -t <target> -g <gateway>"
echo ""
echo "Stress Module:"
echo "  sudo darknet stress syn -t 192.168.1.1 -p 80"
echo "  sudo darknet stress udp -t 192.168.1.1"
echo ""
echo "Packet Module:"
echo "  sudo darknet packet craft --tcp"
echo "  sudo darknet packet sniff -i eth0"
echo ""
echo "====================================="
echo ""
echo "⚠️  IMPORTANT: Always get authorization before testing!"
echo "    Read ETHICAL_GUIDELINES.md for proper use."
echo ""
