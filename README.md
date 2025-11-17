# DarkWiFi - Advanced WiFi Security Testing Tool

**DarkWiFi** is a comprehensive, automated WiFi security testing tool that captures PMKID and EAPOL handshakes, intelligently selects attack methods, and cracks passwords using both aircrack-ng and hashcat.

## Features

- **Intelligent Attack Selection**: Automatically chooses the best attack method based on router capabilities
- **PMKID Capture**: Non-intrusive attack that works on many modern routers
- **EAPOL Handshake Capture**: Automated deauthentication attacks to force handshake capture
- **Dual Cracking**: Supports both aircrack-ng and hashcat for maximum compatibility
- **Personal Wordlist Generator**: Creates targeted wordlists based on personal information about the target
- **Built-in Wordlists**: Includes common password lists
- **Automatic Network Scanning**: Detects security protocols and client presence
- **Virtual Environment**: Self-contained installation with global command access
- **Modern Router Support**: Works against current WPA2/WPA3 implementations

## Installation

### Prerequisites

- Linux system (Kali Linux, Ubuntu, Debian, etc.)
- Python 3.7+
- Root/sudo access

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Ghostyghost43/Darknet.git
cd Darknet

# Run the installation script
chmod +x install.sh
./install.sh
```

The installer will automatically:
- Check for Python 3 and create a virtual environment
- Install required system packages (aircrack-ng, hcxtools, hashcat)
- Install Python dependencies in the venv
- Create a global `darkwifi` command accessible from anywhere
- Set up working directories (captures, wordlists, cracked)

**After installation, verify it works:**
```bash
darkwifi --help
```

You should see the DarkWiFi banner and usage information. You're now ready to start!

### Manual Dependencies

If the automatic installation doesn't work:

```bash
# Install system tools
sudo apt-get update
sudo apt-get install -y aircrack-ng hcxtools hashcat

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Fully Automated Mode (Recommended)

Scan, select target, optionally generate personal wordlist, capture, and crack in one command:

```bash
sudo darkwifi -i wlan0 --auto
```

With personal wordlist generation:

```bash
sudo darkwifi -i wlan0 --auto --personal
```

### Manual Modes

#### 1. Scan for Networks

```bash
sudo darkwifi -i wlan0 --scan
```

#### 2. Capture PMKID

```bash
sudo darkwifi -i wlan0 --pmkid --bssid AA:BB:CC:DD:EE:FF --channel 6 --target "MyNetwork"
```

#### 3. Capture Handshake with Deauth

```bash
sudo darkwifi -i wlan0 --handshake --bssid AA:BB:CC:DD:EE:FF --channel 6 --target "MyNetwork"
```

#### 4. Capture and Crack

```bash
sudo darkwifi -i wlan0 --handshake --bssid AA:BB:CC:DD:EE:FF --channel 6 --target "MyNetwork" --crack --personal
```

#### 5. Crack Existing Capture

```bash
sudo darkwifi --convert captures/handshake_MyNetwork_20240101.cap --crack
```

### Command Line Options

```
-i, --interface INTERFACE   Wireless interface (e.g., wlan0)
--scan                      Scan for networks
--pmkid                     Capture PMKID
--handshake                 Capture EAPOL handshake
--auto                      Fully automated mode (scan + attack + crack)
--target ESSID              Target network name
--bssid BSSID               Target BSSID (MAC address)
--channel CHANNEL           Target channel
--timeout SECONDS           Capture timeout (default: 300)
--wordlist FILE             Custom wordlist for cracking
--personal                  Generate personal wordlist from target info
--crack                     Crack captured hashes
--convert FILE              Convert capture to hashcat format
--no-deauth                 Disable deauth during handshake capture
```

## How It Works

### Intelligent Attack Mode

When you run `--auto`, DarkWiFi follows this intelligent workflow:

1. **Scan**: Discovers nearby networks and detects security protocols
2. **Target Selection**: You choose which network to attack
3. **Personal Intel** (optional): Gathers personal info about target to generate custom wordlist
4. **Strategy 1 - PMKID**:
   - Attempts non-intrusive PMKID capture
   - Works on many routers without deauthenticating clients
   - Silent and undetectable
5. **Strategy 2 - Handshake**:
   - If PMKID fails, captures 4-way handshake
   - Uses deauth attack to force clients to reconnect
   - More reliable but detectable
6. **Conversion**: Automatically converts captures to hashcat format
7. **Cracking**:
   - First tries aircrack-ng
   - Then tries hashcat
   - Uses personal or default wordlist

### Personal Wordlist Generator

The tool asks questions about the target and generates a custom wordlist including:

- Names (first, last, nicknames, family members, pets)
- Important dates (birthdays, anniversaries)
- Numbers (phone numbers, addresses)
- Personal interests (hobbies, favorite teams, colors)
- Common patterns and variations
- Leet speak conversions
- WiFi-specific patterns

This dramatically increases success rate for personal networks.

## Attack Techniques

### PMKID Attack

- Captures Pairwise Master Key Identifier from RSN IE
- Works on WPA/WPA2 networks with roaming features enabled
- No clients required
- Non-intrusive and silent
- Vulnerability: CVE-2018-16385

### Handshake Capture

- Captures 4-way EAPOL handshake
- Requires active clients or deauth attack
- Works on all WPA/WPA2/WPA3 networks with backward compatibility
- More reliable but detectable

## Output Structure

```
Darknet/
├── captures/          # Captured .cap and .pcapng files
├── wordlists/         # Generated and built-in wordlists
├── cracked/           # Successfully cracked passwords
├── venv/              # Python virtual environment
└── *.py               # Tool scripts
```

## Legal & Ethical Use

**IMPORTANT**: This tool is for authorized security testing only.

### Legal Uses:
- Testing your own networks
- Authorized penetration testing with written permission
- Educational purposes in controlled environments
- Security research with proper authorization
- CTF competitions

### Illegal Uses:
- Attacking networks without authorization
- Unauthorized access to computer systems
- Any use that violates local, state, or federal laws

**You are responsible for your actions. Unauthorized access to computer networks is illegal.**

## Troubleshooting

### Interface Not Found

```bash
# List available interfaces
iwconfig

# Ensure wireless card supports monitor mode
iw list | grep -A 10 "Supported interface modes"
```

### Monitor Mode Not Working

```bash
# Kill interfering processes
sudo airmon-ng check kill

# Manually enable monitor mode
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
```

### No PMKID Captured

- Router may not be vulnerable to PMKID attack
- Try handshake capture instead
- Ensure hcxdumptool is installed correctly

### No Handshake Captured

- Ensure clients are connected to the network
- Try increasing timeout: `--timeout 600`
- Move closer to the router
- Check if deauth is working: look for disconnected clients

### Hashcat Not Working

- Ensure hashcat is properly installed
- Try using aircrack-ng instead (automatically attempted first)
- Check GPU drivers if using GPU acceleration

## Advanced Usage

### Using External Wordlists

```bash
# Download rockyou wordlist
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# Use with darkwifi
sudo darkwifi -i wlan0 --auto --wordlist rockyou.txt
```

### Crack Existing Capture Later

```bash
# Generate personal wordlist
python3 wordlist_generator.py

# Crack with personal wordlist
sudo darkwifi --convert captures/my_capture.cap --crack --wordlist wordlists/personal_wordlist.txt
```

### Export for External Cracking

```bash
# Convert to hashcat format
hcxpcapngtool -o hash.22000 captures/my_capture.cap

# Crack on another machine with hashcat
hashcat -m 22000 hash.22000 rockyou.txt
```

## Contributing

Contributions are welcome! Please ensure all additions are for legitimate security testing purposes.

## Disclaimer

This tool is provided for educational and authorized testing purposes only. The authors are not responsible for misuse or damage caused by this tool. Always ensure you have explicit permission before testing any network you do not own.

## Credits

- Built using aircrack-ng suite
- PMKID attack technique by Jens Steube (hashcat)
- hcxtools by ZerBea

## License

For educational and authorized security testing purposes only.
