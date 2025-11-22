# Aircrack-ng Suite - Command Reference

A comprehensive guide to all aircrack-ng tools with common commands and examples.

---

## Table of Contents

1. [airmon-ng](#airmon-ng)
2. [airodump-ng](#airodump-ng)
3. [aireplay-ng](#aireplay-ng)
4. [aircrack-ng](#aircrack-ng)
5. [airbase-ng](#airbase-ng)
6. [airdecap-ng](#airdecap-ng)
7. [airdecloak-ng](#airdecloak-ng)
8. [airdrop-ng](#airdrop-ng)
9. [airgraph-ng](#airgraph-ng)
10. [airolib-ng](#airolib-ng)
11. [airserv-ng](#airserv-ng)
12. [airtun-ng](#airtun-ng)
13. [packetforge-ng](#packetforge-ng)

---

## airmon-ng

**Purpose:** Enable and disable monitor mode on wireless interfaces.

### Basic Commands

```bash
# Check interface status
airmon-ng

# Start monitor mode
airmon-ng start wlan0

# Start on specific channel
airmon-ng start wlan0 6

# Stop monitor mode
airmon-ng stop wlan0mon

# Check for interfering processes
airmon-ng check

# Kill interfering processes
airmon-ng check kill
```

---

## airodump-ng

**Purpose:** Capture raw 802.11 frames and collect wireless network information.

### Basic Commands

```bash
# Scan all networks
airodump-ng wlan0mon

# Scan specific channel
airodump-ng -c 6 wlan0mon

# Scan specific band (a/b/g)
airodump-ng --band abg wlan0mon

# Target specific network (BSSID)
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF wlan0mon

# Save capture to file
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Filter by encryption type
airodump-ng --encrypt wpa2 wlan0mon

# Show WPS information
airodump-ng --wps wlan0mon

# Output in different formats
airodump-ng -w output --output-format pcap,csv,kismet wlan0mon
```

### Output Options

```bash
# GPS coordinates (with gpsd)
airodump-ng --gpsd wlan0mon

# Update interval (in seconds)
airodump-ng --update 2 wlan0mon

# Show only networks with clients
airodump-ng -a wlan0mon
```

---

## aireplay-ng

**Purpose:** Inject and replay wireless frames for various attacks.

### Deauthentication Attack

```bash
# Deauth all clients from AP
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Deauth specific client
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# Continuous deauth (0 = infinite)
aireplay-ng -0 0 -a AA:BB:CC:DD:EE:FF wlan0mon
```

### Fake Authentication

```bash
# Basic fake auth
aireplay-ng -1 0 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Fake auth with reassociation delay
aireplay-ng -1 6000 -o 1 -q 10 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

### ARP Request Replay

```bash
# ARP replay attack
aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

### Chopchop Attack

```bash
# Chopchop attack
aireplay-ng -4 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

### Fragmentation Attack

```bash
# Fragmentation attack
aireplay-ng -5 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

### Injection Test

```bash
# Test injection capability
aireplay-ng -9 wlan0mon

# Test injection to specific AP
aireplay-ng -9 -e "NetworkName" -a AA:BB:CC:DD:EE:FF wlan0mon
```

---

## aircrack-ng

**Purpose:** WEP and WPA/WPA2-PSK key cracking program.

### WPA/WPA2 Cracking

```bash
# Crack with wordlist
aircrack-ng -w wordlist.txt capture.cap

# Specify target BSSID
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture.cap

# Use multiple wordlists
aircrack-ng -w wordlist1.txt,wordlist2.txt capture.cap

# Show ASCII keys only
aircrack-ng -l -w wordlist.txt capture.cap
```

### WEP Cracking

```bash
# Basic WEP crack
aircrack-ng capture.cap

# PTW attack (faster)
aircrack-ng -z capture.cap

# Korek attack
aircrack-ng -K capture.cap

# Specify key length
aircrack-ng -n 64 capture.cap
aircrack-ng -n 128 capture.cap
```

### Advanced Options

```bash
# Use multiple CPU cores
aircrack-ng -p 4 -w wordlist.txt capture.cap

# Use airolib-ng database
aircrack-ng -r database.db capture.cap

# Quiet mode (less output)
aircrack-ng -q -w wordlist.txt capture.cap

# Save cracked key to file
aircrack-ng -w wordlist.txt -l cracked_key.txt capture.cap
```

---

## airbase-ng

**Purpose:** Multi-purpose tool for attacking clients (creates fake APs).

### Basic Fake AP

```bash
# Create open fake AP
airbase-ng -e "FreeWiFi" -c 6 wlan0mon

# Create WEP fake AP
airbase-ng -e "FreeWiFi" -c 6 -W 1 wlan0mon

# Create WPA fake AP
airbase-ng -e "FreeWiFi" -c 6 -Z 2 wlan0mon

# Create WPA2 fake AP
airbase-ng -e "FreeWiFi" -c 6 -Z 4 wlan0mon
```

### Evil Twin Attack

```bash
# Clone existing AP
airbase-ng -e "TargetNetwork" -c 6 -a AA:BB:CC:DD:EE:FF wlan0mon

# With specific BSSID
airbase-ng -e "TargetNetwork" -c 6 -a AA:BB:CC:DD:EE:FF wlan0mon
```

### Advanced Options

```bash
# Respond to all probe requests
airbase-ng -P -C 30 -e "FreeWiFi" -c 6 wlan0mon

# ESSID filtering
airbase-ng -e "FreeWiFi" -c 6 --essid "TargetNetwork" wlan0mon

# Capture to file
airbase-ng -e "FreeWiFi" -c 6 -w capture wlan0mon

# Enable verbose mode
airbase-ng -v -e "FreeWiFi" -c 6 wlan0mon
```

---

## airdecap-ng

**Purpose:** Decrypt WEP/WPA/WPA2 capture files.

### Basic Usage

```bash
# Decrypt WEP capture
airdecap-ng -w HEXKEY capture.cap

# Decrypt WPA/WPA2 capture
airdecap-ng -e "NetworkName" -p password123 capture.cap

# Specify BSSID
airdecap-ng -b AA:BB:CC:DD:EE:FF -p password123 -e "NetworkName" capture.cap
```

### Output Options

```bash
# Remove wireless headers
airdecap-ng -l -e "NetworkName" -p password123 capture.cap

# Output to specific file
airdecap-ng -e "NetworkName" -p password123 -o decrypted.cap capture.cap
```

---

## airdecloak-ng

**Purpose:** Remove WEP Cloaking from a packet capture file.

### Basic Usage

```bash
# Remove cloaking from capture
airdecloak-ng -i cloaked.cap --drop-frag

# Filter by BSSID
airdecloak-ng -i cloaked.cap --bssid AA:BB:CC:DD:EE:FF --drop-frag

# Specify output file
airdecloak-ng -i cloaked.cap -o clean.cap --drop-frag
```

### Filter Options

```bash
# Filter specific filters
airdecloak-ng -i cloaked.cap --filters signal,duplicate --drop-frag
```

---

## airdrop-ng

**Purpose:** Rule-based wireless deauthentication tool.

### Basic Usage

```bash
# Run with rules file
airdrop-ng -i wlan0mon -t clients.csv -r rules.txt

# With airodump output
airdrop-ng -i wlan0mon -t airodump-01.csv -r rules.txt

# Debug mode
airdrop-ng -i wlan0mon -t clients.csv -r rules.txt -d
```

### Rules File Format

```
# Example rules.txt
# Action | Source | Destination | BSSID | ESSID | Channel

d|any|any|AA:BB:CC:DD:EE:FF|any|any
# (d = deny/deauth)

a|11:22:33:44:55:66|any|any|any|any
# (a = allow)
```

---

## airgraph-ng

**Purpose:** Graph wireless networks from airodump-ng output.

### Basic Usage

```bash
# Create CAPR (Client to AP Relationship) graph
airgraph-ng -i dump-01.csv -g CAPR -o network_graph.png

# Create CPG (Common Probe Graph)
airgraph-ng -i dump-01.csv -g CPG -o probe_graph.png
```

### Output Options

```bash
# Specify output format
airgraph-ng -i dump-01.csv -g CAPR -o graph.png

# Filter by ESSID
airgraph-ng -i dump-01.csv -g CAPR --essid "NetworkName" -o graph.png
```

---

## airolib-ng

**Purpose:** Precompute WPA/WPA2 passphrases for faster cracking.

### Database Management

```bash
# Create new database
airolib-ng database.db --init

# Import ESSIDs
airolib-ng database.db --import essid essid_list.txt

# Import passwords
airolib-ng database.db --import passwd wordlist.txt

# Show database stats
airolib-ng database.db --stats
```

### Batch Processing

```bash
# Generate PMKs (precompute)
airolib-ng database.db --batch

# Batch with specific number of threads
airolib-ng database.db --batch --threads 4

# Clean invalid entries
airolib-ng database.db --clean all
```

### Export/Verify

```bash
# Verify database integrity
airolib-ng database.db --verify

# Export to cowpatty format
airolib-ng database.db --export cowpatty "NetworkName" export.cow
```

### Using with aircrack-ng

```bash
# Crack using database
aircrack-ng -r database.db capture.cap
```

---

## airserv-ng

**Purpose:** Wireless card TCP/IP server for remote card access.

### Basic Usage

```bash
# Start server on default port (666)
airserv-ng -d wlan0mon

# Start on specific port
airserv-ng -d wlan0mon -p 1234

# Bind to specific IP
airserv-ng -d wlan0mon -p 1234 -b 192.168.1.100
```

### Client Connection

```bash
# Connect airodump-ng to remote card
airodump-ng 192.168.1.100:1234

# Connect aireplay-ng to remote card
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF 192.168.1.100:1234
```

---

## airtun-ng

**Purpose:** Create virtual tunnel interfaces for wireless traffic.

### WEP Tunnel

```bash
# Create WEP tunnel
airtun-ng -a AA:BB:CC:DD:EE:FF -w HEXKEY wlan0mon

# With specific tunnel name
airtun-ng -a AA:BB:CC:DD:EE:FF -w HEXKEY -t 1 wlan0mon
```

### WPA Tunnel

```bash
# Create WPA tunnel (requires PMKID)
airtun-ng -a AA:BB:CC:DD:EE:FF -p password -e "NetworkName" wlan0mon
```

### Repeater Mode

```bash
# Wireless repeater
airtun-ng -a AA:BB:CC:DD:EE:FF --repeat --bssid BB:CC:DD:EE:FF:00 wlan0mon
```

### IDS Mode

```bash
# Intrusion detection mode
airtun-ng -a AA:BB:CC:DD:EE:FF -w HEXKEY --crypt wlan0mon
```

---

## packetforge-ng

**Purpose:** Create encrypted packets for injection.

### ARP Packets

```bash
# Create ARP request packet
packetforge-ng -0 -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -k 255.255.255.255 -l 255.255.255.255 -y keystream.xor -w arp_packet.cap
```

### Custom Packets

```bash
# Create custom packet from input file
packetforge-ng -9 -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -y keystream.xor -w custom.cap -r input.cap
```

### Null Packets

```bash
# Create null packet
packetforge-ng -1 -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -y keystream.xor -w null.cap
```

### Options

```bash
# -0 : ARP packet
# -1 : NULL packet
# -9 : Custom packet
# -a : AP MAC address
# -h : Source MAC address
# -k : Destination IP
# -l : Source IP
# -y : Keystream file
# -w : Output file
```

---

## Quick Reference Card

| Tool | Purpose | Most Common Command |
|------|---------|---------------------|
| `airmon-ng` | Monitor mode | `airmon-ng start wlan0` |
| `airodump-ng` | Capture packets | `airodump-ng -c 6 --bssid MAC -w cap wlan0mon` |
| `aireplay-ng` | Inject packets | `aireplay-ng -0 10 -a MAC wlan0mon` |
| `aircrack-ng` | Crack keys | `aircrack-ng -w wordlist.txt capture.cap` |
| `airbase-ng` | Fake AP | `airbase-ng -e "Name" -c 6 wlan0mon` |
| `airdecap-ng` | Decrypt captures | `airdecap-ng -e "SSID" -p pass capture.cap` |
| `airdecloak-ng` | Remove cloaking | `airdecloak-ng -i input.cap --drop-frag` |
| `airdrop-ng` | Rule-based deauth | `airdrop-ng -i wlan0mon -t csv -r rules` |
| `airgraph-ng` | Network graphs | `airgraph-ng -i csv -g CAPR -o graph.png` |
| `airolib-ng` | PMK database | `airolib-ng db.db --batch` |
| `airserv-ng` | Remote card | `airserv-ng -d wlan0mon -p 1234` |
| `airtun-ng` | Virtual tunnel | `airtun-ng -a MAC -w KEY wlan0mon` |
| `packetforge-ng` | Create packets | `packetforge-ng -0 -a MAC -h MAC -y xor -w out` |

---

## Important Notes

- Always use these tools only on networks you own or have explicit permission to test
- Running these tools without authorization is illegal in most jurisdictions
- Monitor mode interface names may vary (wlan0mon, wlan1mon, etc.)
- Some tools require root/sudo privileges
- Install aircrack-ng suite: `sudo apt install aircrack-ng`

---

*Generated for authorized security testing and educational purposes only.*
