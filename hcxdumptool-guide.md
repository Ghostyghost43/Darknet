# Complete hcxdumptool Usage Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Prerequisites](#prerequisites)
4. [Basic Usage](#basic-usage)
5. [All Command-Line Options](#all-command-line-options)
6. [Status Messages Explained](#status-messages-explained)
7. [Filtering Options](#filtering-options)
8. [Practical Examples](#practical-examples)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)
11. [Legal Disclaimer](#legal-disclaimer)

---

## Introduction

**hcxdumptool** is a small tool to capture packets from WLAN devices. It's designed to work with hcxtools to convert captured data for use with hashcat or John the Ripper for authorized WiFi security testing.

**Primary Uses:**
- Capture PMKID from access points
- Capture EAPOL handshakes
- WiFi security auditing
- Penetration testing (authorized only)

---

## Installation

### From Source (Recommended)
```bash
git clone https://github.com/ZerBea/hcxdumptool.git
cd hcxdumptool
make
sudo make install
```

### Kali Linux / Debian
```bash
sudo apt update
sudo apt install hcxdumptool
```

### Arch Linux
```bash
sudo pacman -S hcxdumptool
```

---

## Prerequisites

### Hardware Requirements
- WiFi adapter with **monitor mode** support
- Recommended chipsets: Ralink RT3070, Atheros AR9271, Realtek RTL8812AU

### Check Monitor Mode Support
```bash
iw list | grep -A 10 "Supported interface modes"
```

### Required Kernel Headers
```bash
sudo apt install linux-headers-$(uname -r)
```

---

## Basic Usage

### Step 1: Identify Your Wireless Interface
```bash
ip link show
# or
iwconfig
```

### Step 2: Stop Interfering Services
```bash
sudo systemctl stop NetworkManager
sudo systemctl stop wpa_supplicant
sudo airmon-ng check kill
```

### Step 3: Basic Capture Command
```bash
sudo hcxdumptool -i wlan0 -o capture.pcapng
```

### Step 4: Convert Captured Data
```bash
hcxpcapngtool -o hash.22000 capture.pcapng
```

---

## All Command-Line Options

### Interface Options

| Option | Long Form | Description |
|--------|-----------|-------------|
| `-i` | `--interface=<device>` | Specify the wireless interface to use |
| `-o` | `--outfile=<file>` | Output capture file (pcapng format) |
| `-w` | `--write=<file>` | Write raw packets to file |

### Capture Control Options

| Option | Long Form | Description |
|--------|-----------|-------------|
| `-c` | `--channel=<num>` | Set specific channel (1-14 for 2.4GHz, 36-165 for 5GHz) |
| `-t` | `--time=<seconds>` | Capture duration in seconds |
| `-T` | `--staytime=<seconds>` | Time to stay on each channel (default: 5) |
| `--tot` | `--tot=<seconds>` | Total capture time across all channels |

### Channel Options

| Option | Description |
|--------|-------------|
| `--channel=<num>` | Lock to specific channel |
| `--band=<ag>` | Select band: a=5GHz, g=2.4GHz, ag=both |
| `--scan_rounds=<num>` | Number of scan rounds |

### Attack/Capture Mode Options

| Option | Description |
|--------|-------------|
| `--active` | Enable active mode (sends packets) |
| `--passive` | Passive mode only (listen only, no transmit) |
| `--enable_status=<value>` | Enable various status/attack modes (see detailed section below) |
| `--disable_deauthentication` | Don't send deauthentication frames |
| `--disable_disassociation` | Don't send disassociation frames |
| `--disable_ap_attacks` | Don't attack access points |
| `--disable_client_attacks` | Don't attack clients/stations |

### Filtering Options

| Option | Description |
|--------|-------------|
| `--filterlist_ap=<file>` | MAC filter list for access points |
| `--filterlist_client=<file>` | MAC filter list for clients |
| `--filtermode=<num>` | Filter mode: 1=whitelist, 2=blacklist |
| `--essidlist=<file>` | ESSID filter list |
| `--essidmode=<num>` | ESSID mode: 1=whitelist, 2=blacklist |

### GPS Options

| Option | Description |
|--------|-------------|
| `--gpsd` | Enable gpsd support |
| `--nmea=<file>` | NMEA output file |

### Miscellaneous Options

| Option | Description |
|--------|-------------|
| `-h` | `--help` | Show help message |
| `-v` | `--version` | Show version information |
| `--bpf=<file>` | Berkeley Packet Filter file |
| `--errormax=<num>` | Maximum errors before exit |
| `--reboot` | Reboot system on exit |
| `--poweroff` | Power off system on exit |

---

## Status Messages Explained

### Enable Status Values

The `--enable_status=<value>` option controls what information is displayed and what attacks are performed. Values can be combined by adding them together.

| Value | Binary | Name | Description |
|-------|--------|------|-------------|
| 1 | 0x0001 | EAPOL | Show EAPOL (handshake) messages |
| 2 | 0x0002 | PROBEREQUEST | Show probe requests from clients |
| 4 | 0x0004 | PROBERESPONSE | Show probe responses from APs |
| 8 | 0x0008 | AUTH | Show authentication frames |
| 16 | 0x0010 | ASSOC | Show association frames |
| 32 | 0x0020 | REASSOC | Show reassociation frames |
| 64 | 0x0040 | DEAUTH | Show deauthentication frames |
| 128 | 0x0080 | DISASSOC | Show disassociation frames |
| 256 | 0x0100 | BEACON | Show beacon frames |
| 512 | 0x0200 | PMKID | Show PMKID captures |
| 1024 | 0x0400 | EAPOLSTART | Show EAPOL-Start frames |
| 2048 | 0x0800 | PWNAGOTCHI | Pwnagotchi detection |
| 4096 | 0x1000 | ATIM | Show ATIM frames (ad-hoc) |
| 8192 | 0x2000 | ACTION | Show action frames |
| 16384 | 0x4000 | EAPOLPMKID | Show EAPOL with PMKID |
| 32768 | 0x8000 | RX | Show all received frames |

### Common Status Combinations

```bash
# Show EAPOL and PMKID only (most common)
--enable_status=513

# Show everything important for WPA capture
--enable_status=31743

# Verbose mode - show all
--enable_status=65535

# PMKID focused
--enable_status=512

# Handshake focused
--enable_status=1

# Show probes and beacons (passive recon)
--enable_status=262
```

### Console Output Status Indicators

During capture, you'll see various status indicators:

| Symbol/Text | Meaning |
|-------------|---------|
| `[FOUND PMKID]` | Successfully captured PMKID from AP |
| `[FOUND HANDSHAKE]` | Captured complete EAPOL handshake |
| `[EAPOL M1]` | Captured Message 1 of 4-way handshake |
| `[EAPOL M2]` | Captured Message 2 of 4-way handshake |
| `[EAPOL M3]` | Captured Message 3 of 4-way handshake |
| `[EAPOL M4]` | Captured Message 4 of 4-way handshake |
| `[BEACON]` | Received beacon from AP |
| `[PROBERESPONSE]` | AP responded to probe |
| `[PROBEREQUEST]` | Client searching for network |
| `[AUTHENTICATION]` | Authentication frame captured |
| `[ASSOCIATION]` | Association request/response |
| `[REASSOCIATION]` | Client reassociating |
| `[DEAUTHENTICATION]` | Deauth frame (sent or received) |
| `[DISASSOCIATION]` | Disassociation frame |
| `[EAPOLSTART]` | Client initiated EAPOL |

### Attack Status Messages

| Message | Meaning |
|---------|---------|
| `ATTACKING` | Currently sending attack frames to target |
| `TRANSMITTING` | Sending packets |
| `RX/TX` | Receiving/Transmitting indicator |
| `SKIP` | Target skipped (already captured or filtered) |
| `RETRY` | Retrying attack on target |

---

## Filtering Options

### MAC Address Filtering

#### Create a Whitelist (Target Only These)
```bash
# Create filter file with target MACs (one per line)
echo "AA:BB:CC:DD:EE:FF" > targets.txt
echo "11:22:33:44:55:66" >> targets.txt

# Use whitelist for APs
sudo hcxdumptool -i wlan0 -o capture.pcapng --filterlist_ap=targets.txt --filtermode=1
```

#### Create a Blacklist (Exclude These)
```bash
# Create blacklist
echo "AA:BB:CC:DD:EE:FF" > exclude.txt

# Use blacklist
sudo hcxdumptool -i wlan0 -o capture.pcapng --filterlist_ap=exclude.txt --filtermode=2
```

### ESSID Filtering

#### Target Specific Networks by Name
```bash
# Create ESSID list
echo "TargetNetwork" > essids.txt
echo "AnotherNetwork" >> essids.txt

# Whitelist mode
sudo hcxdumptool -i wlan0 -o capture.pcapng --essidlist=essids.txt --essidmode=1

# Blacklist mode
sudo hcxdumptool -i wlan0 -o capture.pcapng --essidlist=essids.txt --essidmode=2
```

### BPF (Berkeley Packet Filter)

For advanced filtering using BPF syntax:
```bash
# Create BPF file
echo "wlan type mgt subtype beacon" > filter.bpf

# Apply filter
sudo hcxdumptool -i wlan0 -o capture.pcapng --bpf=filter.bpf
```

---

## Practical Examples

### Example 1: Basic PMKID Capture
```bash
# Stop interfering services
sudo systemctl stop NetworkManager wpa_supplicant

# Capture with PMKID status enabled
sudo hcxdumptool -i wlan0 -o pmkid_capture.pcapng --enable_status=512

# Convert to hashcat format
hcxpcapngtool -o hashes.22000 pmkid_capture.pcapng
```

### Example 2: Target Specific Channel
```bash
# Capture on channel 6 only
sudo hcxdumptool -i wlan0 -o ch6_capture.pcapng -c 6 --enable_status=31743
```

### Example 3: Time-Limited Capture
```bash
# Capture for 5 minutes (300 seconds)
sudo hcxdumptool -i wlan0 -o timed_capture.pcapng -t 300 --enable_status=513
```

### Example 4: Passive Mode Only (No Attacks)
```bash
# Pure passive capture - no deauth/disassoc attacks
sudo hcxdumptool -i wlan0 -o passive.pcapng --passive --enable_status=65535
```

### Example 5: Target Specific AP
```bash
# Create target file
echo "AA:BB:CC:DD:EE:FF" > target_ap.txt

# Target only that AP
sudo hcxdumptool -i wlan0 -o target.pcapng \
  --filterlist_ap=target_ap.txt \
  --filtermode=1 \
  --enable_status=513
```

### Example 6: 5GHz Band Only
```bash
# Capture on 5GHz band
sudo hcxdumptool -i wlan0 -o 5ghz_capture.pcapng --band=a --enable_status=513
```

### Example 7: Both Bands with Longer Channel Dwell
```bash
# Both bands, 10 seconds per channel
sudo hcxdumptool -i wlan0 -o dual_band.pcapng \
  --band=ag \
  --staytime=10 \
  --enable_status=513
```

### Example 8: Full Verbose Capture
```bash
# Everything enabled, all status
sudo hcxdumptool -i wlan0 -o verbose.pcapng \
  --enable_status=65535 \
  --band=ag
```

### Example 9: GPS-Enabled Wardriving
```bash
# Start gpsd first
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

# Capture with GPS
sudo hcxdumptool -i wlan0 -o wardriving.pcapng \
  --gpsd \
  --enable_status=513
```

### Example 10: Exclude Your Own Networks
```bash
# List your networks to exclude
echo "MyHomeWifi" > exclude_essids.txt
echo "MyPhoneHotspot" >> exclude_essids.txt

# Capture excluding your networks
sudo hcxdumptool -i wlan0 -o capture.pcapng \
  --essidlist=exclude_essids.txt \
  --essidmode=2 \
  --enable_status=513
```

### Example 11: Capture Without Deauthentication
```bash
# Gentler approach - no deauth attacks
sudo hcxdumptool -i wlan0 -o no_deauth.pcapng \
  --disable_deauthentication \
  --enable_status=513
```

### Example 12: Maximum Stealth Passive Recon
```bash
# Complete passive mode for reconnaissance
sudo hcxdumptool -i wlan0 -o recon.pcapng \
  --passive \
  --disable_deauthentication \
  --disable_disassociation \
  --disable_ap_attacks \
  --disable_client_attacks \
  --enable_status=262
```

---

## Advanced Usage

### Channel Hopping Strategy

```bash
# Fast hopping (2 seconds per channel)
sudo hcxdumptool -i wlan0 -o fast.pcapng --staytime=2 --enable_status=513

# Slow hopping (20 seconds per channel)
sudo hcxdumptool -i wlan0 -o slow.pcapng --staytime=20 --enable_status=513

# Multiple scan rounds
sudo hcxdumptool -i wlan0 -o multi.pcapng --scan_rounds=3 --enable_status=513
```

### Combining with hcxtools

#### Complete Workflow
```bash
# 1. Capture
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=513 -t 600

# 2. Convert to hashcat format (mode 22000)
hcxpcapngtool -o hashes.22000 capture.pcapng

# 3. View capture statistics
hcxpcapngtool --info=stdout capture.pcapng

# 4. Extract specific hash types
# PMKID only
hcxpcapngtool -o pmkid.22000 --pmkid capture.pcapng

# EAPOL only
hcxpcapngtool -o eapol.22000 --eapol capture.pcapng
```

### Running as Background Service

```bash
# Start in background with nohup
nohup sudo hcxdumptool -i wlan0 -o long_capture.pcapng \
  --enable_status=513 \
  --tot=86400 > /dev/null 2>&1 &

# Or use systemd service (create /etc/systemd/system/hcxdumptool.service)
```

### Auto-Shutdown on Completion

```bash
# Power off after capture
sudo hcxdumptool -i wlan0 -o capture.pcapng -t 3600 --poweroff

# Reboot after capture
sudo hcxdumptool -i wlan0 -o capture.pcapng -t 3600 --reboot
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Could not find specified interface"
```bash
# Check available interfaces
ip link show

# Bring interface up
sudo ip link set wlan0 up
```

#### Issue: "Interface already in use"
```bash
# Kill interfering processes
sudo airmon-ng check kill

# Or manually stop services
sudo systemctl stop NetworkManager
sudo systemctl stop wpa_supplicant
sudo killall wpa_supplicant
```

#### Issue: "No PMKIDs or handshakes captured"
- Ensure you're in range of targets
- Try longer dwell time: `--staytime=15`
- Try specific channel if you know target's channel
- Some APs don't respond to PMKID requests (try handshake capture instead)

#### Issue: "Operation not permitted"
```bash
# Run with sudo
sudo hcxdumptool ...

# Check capabilities
getcap /usr/bin/hcxdumptool
```

#### Issue: "Monitor mode not supported"
- Your adapter doesn't support monitor mode
- Try: `sudo iw dev wlan0 set type monitor`
- Use a compatible adapter (see prerequisites)

#### Issue: High Error Count
```bash
# Set error threshold
sudo hcxdumptool -i wlan0 -o capture.pcapng --errormax=100 --enable_status=513
```

### Checking Capture File

```bash
# Verify capture has data
hcxpcapngtool --info=stdout capture.pcapng

# Check hash count
hcxpcapngtool -o test.22000 capture.pcapng && wc -l test.22000

# View with Wireshark
wireshark capture.pcapng
```

### Interface Recovery After Capture

```bash
# Restart NetworkManager
sudo systemctl start NetworkManager

# Or manually restore managed mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up
```

---

## Quick Reference Card

### Most Common Commands

```bash
# Basic capture
sudo hcxdumptool -i wlan0 -o output.pcapng --enable_status=513

# Passive only
sudo hcxdumptool -i wlan0 -o output.pcapng --passive --enable_status=513

# Specific channel
sudo hcxdumptool -i wlan0 -o output.pcapng -c 6 --enable_status=513

# Time limited
sudo hcxdumptool -i wlan0 -o output.pcapng -t 300 --enable_status=513

# Target specific AP
sudo hcxdumptool -i wlan0 -o output.pcapng --filterlist_ap=target.txt --filtermode=1 --enable_status=513
```

### Enable Status Quick Reference

| Goal | Value | Command |
|------|-------|---------|
| PMKID Only | 512 | `--enable_status=512` |
| Handshakes Only | 1 | `--enable_status=1` |
| Both PMKID & Handshakes | 513 | `--enable_status=513` |
| Passive Recon | 262 | `--enable_status=262` |
| Everything | 65535 | `--enable_status=65535` |

### File Extensions

| Extension | Purpose |
|-----------|---------|
| `.pcapng` | Capture file format |
| `.22000` | Hashcat hash format |
| `.hc22000` | Alternative hashcat format |

---

## Legal Disclaimer

⚠️ **IMPORTANT: Legal and Ethical Use Only**

hcxdumptool is a powerful tool designed for **authorized security testing only**.

### Legal Requirements:
- **Only use on networks you own or have explicit written permission to test**
- Unauthorized access to computer networks is illegal in most jurisdictions
- Violations may result in criminal prosecution and civil liability

### Authorized Use Cases:
- ✅ Testing your own home/business network security
- ✅ Authorized penetration testing with written permission
- ✅ Educational purposes in controlled lab environments
- ✅ Security research with proper authorization

### Prohibited Uses:
- ❌ Accessing networks without authorization
- ❌ Capturing data from neighbors' networks
- ❌ Any activity without explicit permission

**The user assumes all responsibility for complying with applicable laws.**

---

## Additional Resources

- [hcxdumptool GitHub Repository](https://github.com/ZerBea/hcxdumptool)
- [hcxtools GitHub Repository](https://github.com/ZerBea/hcxtools)
- [Hashcat Wiki](https://hashcat.net/wiki/)
- [Kali Linux Documentation](https://www.kali.org/docs/)

---

*Guide Version: 1.0*
*Last Updated: 2025*
