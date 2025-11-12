#!/bin/bash
#
# Darknet Demo - Network Scanning
# Demonstrates basic scanning capabilities
#

if [ "$EUID" -ne 0 ]; then
    echo "[!] This demo requires root privileges"
    echo "[*] Run: sudo $0"
    exit 1
fi

echo "====================================="
echo "Darknet Framework - Scanning Demo"
echo "====================================="
echo ""
echo "This demo shows basic scanning features."
echo "Note: Most features are stubs and for demonstration only."
echo ""

# Check if darknet is installed
if ! command -v darknet &> /dev/null; then
    echo "[!] Darknet not found. Using local binary..."
    DARKNET="./bin/darknet"
    if [ ! -f "$DARKNET" ]; then
        echo "[!] Please build Darknet first: make"
        exit 1
    fi
else
    DARKNET="darknet"
fi

# Demo commands
echo "[*] Listing available scan modules..."
$DARKNET modules | grep -A 10 "Network Scanning"

echo ""
echo "[*] Testing scan help..."
$DARKNET scan --help

echo ""
echo "[*] Demo: Port scan (stub)"
echo "    Command: darknet scan ports -t 192.168.1.1 -p 1-1000"
$DARKNET scan ports

echo ""
echo "[*] Demo: Ping sweep (stub)"
echo "    Command: darknet scan ping -r 192.168.1.0/24"
$DARKNET scan ping

echo ""
echo "====================================="
echo "Demo Complete"
echo "====================================="
echo ""
echo "To implement real scanning:"
echo "  1. Complete the scan module implementations"
echo "  2. Add libpcap support"
echo "  3. Implement raw socket operations"
echo ""
echo "Always get authorization before scanning!"
