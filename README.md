# 🕵️ Darknet - Counter-Intelligence Device Scanner

A powerful, feature-rich tool for detecting and tracking nearby devices to identify potential surveillance, tracking, or stalking attempts. Built for Linux, Kali Linux, and Raspberry Pi.

## 🎯 Overview

**Darknet** is a defensive security tool that continuously scans for WiFi and Bluetooth devices in your vicinity, tracks them over time, and alerts you to suspicious patterns that may indicate:

- 📍 **Location Tracking** - Devices following you to multiple locations
- 👁️ **Surveillance** - Devices appearing repeatedly at different times
- 🚨 **Stalking/Tracking Devices** - AirTags, Tiles, hidden trackers
- 📡 **Proximity Monitoring** - Devices getting closer to you
- ⏰ **Scheduled Surveillance** - Devices appearing at consistent times

## ✨ Features

### Core Capabilities
- **WiFi Scanning** - Detects access points, phones, laptops, and WiFi-enabled devices
- **Bluetooth Scanning** - Identifies BT Classic and BLE devices including trackers
- **Continuous Monitoring** - Background scanning with configurable intervals
- **Pattern Detection** - AI-powered analysis to identify suspicious behavior
- **Threat Scoring** - Automatic threat level assessment (LOW/MEDIUM/HIGH/CRITICAL)
- **Alert System** - Real-time notifications for high-risk devices
- **Device Database** - SQLite database tracks all devices and sightings
- **Interactive CLI** - Easy-to-use command-line interface

### Detection Patterns
The tool analyzes multiple patterns to identify threats:
- **Multiple Sightings** - Same device seen repeatedly
- **Multi-Location Tracking** - Device appears at different locations
- **Signal Strength Analysis** - Device getting closer/following you
- **Temporal Patterns** - Scheduled surveillance (same times/days)
- **Activity Bursts** - Sudden increase in sightings

### Tracker Detection
Specifically detects known tracking devices:
- Apple AirTags
- Tile trackers
- Samsung Galaxy SmartTag
- Chipolo trackers
- Generic Bluetooth trackers

## 🚀 Installation

### Prerequisites
- Linux-based OS (Kali Linux, Raspberry Pi OS, Ubuntu, Debian)
- Python 3.7 or higher
- Root/sudo privileges (for full functionality)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/Darknet.git
cd Darknet

# Run the installation script
chmod +x install.sh
./install.sh
```

The installation script will:
1. Install system dependencies (wireless-tools, aircrack-ng, bluez)
2. Create a Python virtual environment
3. Install all required Python packages
4. Set up directories and permissions
5. Create a launcher script

### Manual Installation

If you prefer manual installation:

```bash
# Install system packages (Debian/Ubuntu/Kali/Raspberry Pi)
sudo apt-get update
sudo apt-get install -y wireless-tools iw aircrack-ng bluez bluetooth
sudo apt-get install -y python3 python3-pip python3-venv python3-dev
sudo apt-get install -y build-essential libpcap-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
chmod +x darknet.py install.sh
```

## 📖 Usage

### Running Darknet

```bash
# Using the launcher (recommended)
./run.sh

# Or manually with venv
source venv/bin/activate
sudo python3 darknet.py
```

**Important:** Always run with sudo/root for full functionality (WiFi monitor mode, Bluetooth scanning).

### Interactive Commands

Once Darknet is running, you'll see an interactive prompt. Available commands:

#### Scanning Commands
```
scan              - Run a single scan (WiFi + Bluetooth)
scan wifi         - Scan WiFi only
scan bluetooth    - Scan Bluetooth only
monitor           - Start continuous monitoring (scans at intervals)
```

#### Information Commands
```
list              - List all detected devices
threats           - Show threat analysis for suspicious devices
alerts            - Show recent alerts
stats             - Show statistics summary
```

#### Device Commands
```
device <mac>      - Show detailed information for a specific device
analyze <mac>     - Run threat analysis on a specific device
note <mac> <text> - Add a note to a device
```

#### Utility Commands
```
export            - Export data to file
clear             - Clear screen
help              - Show help information
exit              - Exit program
```

### Example Session

```bash
$ ./run.sh

╔══════════════════════════════════════════════════════════════╗
║         Darknet Counter-Intelligence Device Scanner         ║
╚══════════════════════════════════════════════════════════════╝

darknet> scan
============================================================
Starting scan: ALL
============================================================

[*] Scanning WiFi...
  [+] ACCESS_POINT: 00:14:22:AB:CD:EF (Dell Inc.) - HomeNetwork
  [+] STATION: B8:27:EB:12:34:56 (Raspberry Pi) - Unknown
✓ WiFi scan complete: 2 devices found

[*] Scanning Bluetooth...
  [+] PHONE: 1A:2B:3C:4D:5E:6F - John's iPhone
  [!!! TRACKER ALERT !!!] AA:BB:CC:DD:EE:FF - AirTag
✓ Bluetooth scan complete: 2 devices found

Scan complete: 4 total devices found

darknet> threats
============================================================
THREAT ANALYSIS - 1 Suspicious Device
============================================================

[HIGH] AA:BB:CC:DD:EE:FF
  Type: BLUETOOTH | Vendor: Apple
  Seen: 5 times | Last: 2025-11-18 16:30
  Threat Score: 35
  Suspicious Patterns:
    • [HIGH] Device seen at 3 different locations
    • [MEDIUM] Device seen 5 times
  Recommendations:
    → ⚠️  HIGH RISK: Consider taking immediate action
    → 🚨 TRACKING CONFIRMED: Device seen at multiple locations
    → Document all sightings with timestamps and locations

darknet> monitor
Starting continuous monitoring...
Scan interval: 60 seconds
Press Ctrl+C to stop
```

## ⚙️ Configuration

Configuration file: `config/default_config.yaml`

```yaml
# Database settings
db_path: "data/devices.db"

# WiFi scanning
wifi_interface: null  # Auto-detect if null
wifi_scan_method: "auto"  # auto, scapy, or iwlist
wifi_scan_duration: 10  # seconds

# Bluetooth scanning
bt_adapter: "hci0"
bt_scan_duration: 10  # seconds

# Monitoring
scan_interval: 60  # seconds between scans

# Threat detection thresholds
threat_thresholds:
  low: 2
  medium: 4
  high: 7
  critical: 11
```

## 🔧 Advanced Usage

### WiFi Monitor Mode

For advanced WiFi scanning (detecting all devices, not just APs):

```bash
# Enable monitor mode (requires root)
sudo airmon-ng start wlan0

# Run Darknet with monitor interface
sudo python3 darknet.py
```

### Custom Configuration

```bash
# Use custom config file
./darknet.py --config /path/to/custom_config.yaml
```

### Running on Raspberry Pi

Darknet works great on Raspberry Pi for portable surveillance detection:

```bash
# On Raspberry Pi, ensure Bluetooth is enabled
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Run Darknet
./run.sh
```

## 🛡️ Use Cases

### Personal Security
- Detect if someone is tracking your movements
- Identify hidden AirTags or Tile trackers on your vehicle/belongings
- Monitor for surveillance devices at your home or office

### Travel Safety
- Detect tracking devices at hotels or rental properties
- Monitor for surveillance during travel
- Identify suspicious devices following you

### Privacy Protection
- Regular scans to ensure no tracking devices nearby
- Verify rental cars don't have tracking devices
- Check Airbnb/hotel rooms for monitoring devices

### Security Research
- Study device behavior patterns
- Test tracking device detection methods
- Analyze surveillance techniques

## 📊 Understanding Threat Levels

- **LOW** - Device seen 2-3 times (might be coincidence)
- **MEDIUM** - Device seen 4-6 times (worth monitoring)
- **HIGH** - Device seen 7-10 times OR appears at multiple locations (likely tracking)
- **CRITICAL** - Device seen 11+ times OR active surveillance patterns detected

## ⚠️ Legal & Ethical Notice

**This tool is for legitimate defensive security purposes only:**

✅ **Authorized Uses:**
- Personal security and privacy protection
- Detecting unauthorized tracking devices
- Security research and education
- Authorized penetration testing
- CTF competitions

❌ **Prohibited Uses:**
- Unauthorized surveillance of others
- Stalking or harassment
- Violation of privacy laws
- Any illegal activities

**Always comply with local laws regarding wireless monitoring and privacy.**

## 🔍 How It Works

### Scanning Process
1. **WiFi Scanning** - Uses `scapy` (monitor mode) or `iwlist` to detect WiFi devices
2. **Bluetooth Scanning** - Uses `bluetoothctl`, `hcitool`, and BLE scanning
3. **Data Storage** - All devices stored in SQLite database with timestamps
4. **Pattern Analysis** - AI algorithms analyze sighting patterns
5. **Threat Assessment** - Scoring based on multiple suspicious indicators
6. **Alerting** - Real-time notifications for high-risk devices

### Pattern Detection Algorithms
- **Frequency Analysis** - How often device appears
- **Location Correlation** - Same device at different places
- **Temporal Analysis** - Time-based patterns
- **Proximity Tracking** - Signal strength trends
- **Burst Detection** - Sudden increase in activity

## 🐛 Troubleshooting

### "Not running as root" warning
- Run with `sudo`: `sudo ./run.sh`
- Required for WiFi monitor mode and Bluetooth scanning

### WiFi scanning not working
- Check interface: `iwconfig` or `ip link show`
- Enable monitor mode: `sudo airmon-ng start wlan0`
- Try iwlist method: Set `wifi_scan_method: "iwlist"` in config

### Bluetooth not detecting devices
- Check Bluetooth: `sudo systemctl status bluetooth`
- Enable adapter: `sudo hciconfig hci0 up`
- Scan manually: `sudo hcitool scan`

### Permission denied errors
- Ensure running with sudo/root
- Check file permissions: `chmod +x darknet.py install.sh`

### Python package errors
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`
- Update pip: `pip install --upgrade pip`

## 📁 Project Structure

```
Darknet/
├── darknet.py              # Main entry point
├── run.sh                  # Launcher script
├── install.sh              # Installation script
├── requirements.txt        # Python dependencies
├── config/
│   └── default_config.yaml # Configuration file
├── src/
│   ├── core/
│   │   ├── database.py     # Device database management
│   │   ├── config.py       # Configuration management
│   │   ├── cli.py          # Interactive CLI
│   │   └── pattern_detector.py  # Threat analysis
│   └── scanners/
│       ├── wifi_scanner.py      # WiFi scanning
│       └── bluetooth_scanner.py # Bluetooth scanning
├── data/                   # Database files
└── logs/                   # Log files
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is for educational and defensive security purposes. Use responsibly and legally.

## 🙏 Acknowledgments

Built with:
- [Scapy](https://scapy.net/) - Packet manipulation
- [BlueZ](http://www.bluez.org/) - Bluetooth stack
- [Colorama](https://github.com/tartley/colorama) - Terminal colors
- [Tabulate](https://github.com/astanin/python-tabulate) - Table formatting

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Stay Safe. Stay Private. Use Darknet.** 🛡️
