# Darknet - WiFi Deauth Tool

A simple C-based WiFi deauthentication tool for security testing and educational purposes.

## ⚠️ Legal Warning

**This tool is for educational and authorized security testing ONLY.**

Unauthorized access to computer networks is illegal. Only use this tool on:
- Networks you own
- Networks you have explicit written permission to test
- Controlled lab environments for educational purposes

Misuse of this tool may violate laws including the Computer Fraud and Abuse Act (CFAA) in the US and similar laws in other jurisdictions.

## Features

- Simple C implementation
- IEEE 802.11 deauthentication frame generation
- Customizable target and AP MAC addresses
- Configurable frame count
- Minimal dependencies

## Requirements

- Linux operating system
- Wireless adapter supporting monitor mode
- Root/sudo privileges
- GCC compiler

## Compilation

```bash
# Using Makefile
make

# Or manually
gcc -o deauth deauth.c
```

## Usage

### 1. Put your wireless interface in monitor mode

```bash
sudo airmon-ng start wlan0
# This creates wlan0mon interface
```

### 2. Run the deauth tool

```bash
sudo ./deauth <interface> <target_mac> <ap_mac> [count]
```

**Arguments:**
- `interface` - Wireless interface in monitor mode (e.g., wlan0mon)
- `target_mac` - Target client MAC address (e.g., AA:BB:CC:DD:EE:FF)
- `ap_mac` - Access Point MAC address (e.g., 11:22:33:44:55:66)
- `count` - Number of deauth frames to send (optional, default: 10)

### Example

```bash
sudo ./deauth wlan0mon AA:BB:CC:DD:EE:FF 11:22:33:44:55:66 20
```

## How It Works

The tool sends IEEE 802.11 deauthentication frames to disconnect a client from an access point:

1. Creates a raw packet socket
2. Constructs a valid 802.11 deauth frame
3. Sends the frame to the specified target
4. The client receives the deauth and disconnects

## Technical Details

- **Frame Type**: 0xC0 (Deauthentication)
- **Reason Code**: 0x0007 (Class 3 frame from non-associated station)
- **Default Delay**: 100ms between frames

## Educational Purpose

This tool is designed to teach:
- Raw socket programming in C
- IEEE 802.11 frame structure
- WiFi security vulnerabilities
- Network packet manipulation

## Limitations

- Requires monitor mode capability
- Only works with 2.4GHz/5GHz networks
- May not work with 802.11w (Protected Management Frames)
- Requires root privileges

## Defense Against Deauth Attacks

- Use WPA3 with Protected Management Frames (PMF/802.11w)
- Enable wireless intrusion detection systems (WIDS)
- Monitor for excessive deauth frames
- Use hidden SSIDs (limited protection)

## License

Educational use only. Use responsibly and legally.

## Disclaimer

The authors are not responsible for any misuse of this tool. Users are solely responsible for ensuring they have proper authorization before using this tool on any network.
