# Darknet Wireless Security Framework

```
╔═══════════════════════════════════════════════════════════════╗
║  ██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗  ║
║  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝  ║
║  ██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║     ║
║  ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║     ║
║  ██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║     ║
║  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝     ║
║                                                                 ║
║        Advanced Wireless Security Framework v1.0.0             ║
╚═══════════════════════════════════════════════════════════════╝
```

**Darknet** is a comprehensive wireless security framework combining the power of Metasploit and Bettercap, designed for authorized penetration testing, security research, and network defense. It features aggressive offensive capabilities alongside robust defensive monitoring and detection systems.

---

## ⚠️ LEGAL DISCLAIMER

**FOR AUTHORIZED SECURITY TESTING ONLY**

This tool is designed exclusively for:
- Authorized penetration testing engagements
- Security research in controlled environments
- Educational purposes in legitimate security training
- Defensive security operations and monitoring

**Unauthorized use of this tool against networks you don't own or have explicit permission to test is ILLEGAL and may result in criminal prosecution.**

---

## 🌟 Features

### 🔴 Red Team Capabilities

#### Wireless Attacks
- **Deauthentication Attacks** - Aggressive client disconnection (up to 200 packets/sec)
- **Disassociation Attacks** - Alternative disconnection method
- **Evil Twin** - Rogue AP creation with automated credential capture
- **PMKID Capture** - Clientless WPA/WPA2 cracking (CVE-2018-16385)
- **Handshake Capture** - WPA/WPA2 4-way handshake capture with auto-deauth
- **Beacon Flood** - MDK4-style AP flooding (create thousands of fake APs)
- **Authentication Flood** - MDK4-style authentication DoS
- **Probe Request Flooding** - Client tracking and DoS

#### MITM Attacks (Bettercap-style)
- **ARP Spoofing** - Man-in-the-middle via ARP poisoning
- **DNS Spoofing** - Intercept and forge DNS responses
- **Packet Sniffing** - Capture credentials, cookies, and HTTP traffic
- **SSL Stripping** - Downgrade HTTPS to HTTP
- **Traffic Analysis** - Real-time protocol analysis

#### Network Attacks
- **Physical Layer** - Channel manipulation, jamming detection
- **Network Layer** - IP-based attacks and scanning
- **Application Layer** - Protocol-specific attacks

### 🔵 Blue Team Capabilities

#### Intrusion Detection
- **Wireless IDS** - Comprehensive threat detection
- **Deauth Detection** - Real-time deauthentication attack alerts
- **Evil Twin Detection** - Rogue AP and duplicate SSID detection
- **Beacon Flood Detection** - Identify beacon flooding attacks
- **Probe Flood Detection** - Detect reconnaissance activities
- **Handshake Capture Detection** - Alert on potential credential harvesting

#### Monitoring & Analysis
- **Real-time Monitoring** - Live wireless network monitoring
- **Threat Alerting** - Severity-based alert system
- **Traffic Analysis** - Protocol distribution and anomaly detection
- **Device Tracking** - AP and client tracking with associations

### 🛠️ Core Features

- **Interface Management** - Automated monitor mode, MAC randomization
- **Wireless Scanning** - Comprehensive AP and client discovery
- **Network Scanning** - Local network host discovery
- **Channel Hopping** - Multi-channel monitoring
- **Packet Injection** - High-speed packet injection (200+ pps)
- **Matrix Theme** - Green-on-black terminal aesthetic
- **Rich Logging** - Detailed logging with multiple output formats

---

## 📋 Requirements

### System Requirements
- **OS**: Linux (Kali Linux, Parrot OS, Ubuntu, Debian, Arch)
- **Python**: 3.8+
- **Privileges**: Root access required

### Hardware Requirements
- Wireless adapter with **monitor mode** support
- Wireless adapter with **packet injection** support
- Recommended chipsets: Atheros, Ralink, Realtek (rtl8812au)

### System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y \
    aircrack-ng \
    iw \
    wireless-tools \
    net-tools \
    python3 \
    python3-pip \
    build-essential \
    tcpdump
```

---

## 🚀 Installation

### Quick Install
```bash
# Clone repository
git clone https://github.com/codypratt88/Darknet.git
cd Darknet

# Install dependencies
sudo pip3 install -r requirements.txt

# Install Darknet
sudo python3 setup.py install

# Or install in development mode
sudo pip3 install -e .
```

### Verify Installation
```bash
darknet --version
darknet interfaces
```

---

## 💻 Usage

### Basic Commands

#### List Wireless Interfaces
```bash
sudo darknet interfaces
```

#### Scan for Networks
```bash
# Basic scan
sudo darknet scan -i wlan0

# Extended scan with custom duration
sudo darknet scan -i wlan0 -d 60

# Scan without channel hopping
sudo darknet scan -i wlan0 --no-channel-hop
```

### Offensive Operations

#### Deauthentication Attack
```bash
# Broadcast deauth (disconnect all clients)
sudo darknet deauth -i wlan0 -a 00:11:22:33:44:55

# Targeted deauth
sudo darknet deauth -i wlan0 -a 00:11:22:33:44:55 -c AA:BB:CC:DD:EE:FF

# Aggressive deauth
sudo darknet deauth -i wlan0 -a 00:11:22:33:44:55 -n 200 -r 200
```

#### Evil Twin Attack
```bash
sudo darknet evil-twin -i wlan0 -s "FreeWiFi" -a 00:11:22:33:44:55 -c 6
```

#### PMKID Capture
```bash
darknet pmkid -i wlan0 -a 00:11:22:33:44:55 -s "TargetNetwork"
```

#### Handshake Capture
```bash
darknet handshake -i wlan0 -a 00:11:22:33:44:55 -s "TargetNetwork" -c 6
```

#### Beacon Flood
```bash
# Create 1000 fake APs
sudo darknet beacon-flood -i wlan0 -n 1000 -r 200
```

### MITM Operations

#### ARP Spoofing
```bash
sudo darknet arp-spoof -i eth0 -t 192.168.1.100 -g 192.168.1.1
```

#### DNS Spoofing
```bash
# Spoof specific domain
sudo darknet dns-spoof -i eth0 -d example.com -ip 192.168.1.50

# Wildcard spoofing
sudo darknet dns-spoof -i eth0 -ip 192.168.1.50 --wildcard
```

#### Packet Sniffing
```bash
sudo darknet sniff -i eth0 --passwords --cookies --urls
```

### Defensive Operations

#### Wireless IDS
```bash
# Start IDS with default settings
sudo darknet ids -i wlan0

# Custom thresholds
sudo darknet ids -i wlan0 --deauth-threshold 20 --beacon-threshold 150
```

---

## 🎯 Common Attack Scenarios

### Scenario 1: WPA2 Handshake Capture
```bash
# 1. Enable monitor mode and scan
sudo darknet scan -i wlan0 -d 30

# 2. Capture handshake with auto-deauth
sudo darknet handshake -i wlan0 -a TARGET_AP_MAC -s "NetworkName" -c 6

# 3. Crack with hashcat or aircrack-ng
hashcat -m 22000 handshake.hccapx wordlist.txt
```

### Scenario 2: Evil Twin with Credential Capture
```bash
# 1. Deauth clients from real AP
sudo darknet deauth -i wlan0 -a REAL_AP_MAC &

# 2. Start evil twin
sudo darknet evil-twin -i wlan1 -s "CoffeeShopWiFi" -c 6

# 3. Clients will connect to your AP and attempt authentication
```

### Scenario 3: Network MITM
```bash
# 1. ARP spoof target
sudo darknet arp-spoof -i eth0 -t 192.168.1.100 -g 192.168.1.1 &

# 2. DNS spoof for phishing
sudo darknet dns-spoof -i eth0 -d bank.com -ip 192.168.1.50 &

# 3. Sniff credentials
sudo darknet sniff -i eth0
```

### Scenario 4: Network Defense
```bash
# Monitor for attacks
sudo darknet ids -i wlan0

# The IDS will alert on:
# - Deauth attacks
# - Evil twin/rogue APs
# - Beacon floods
# - Handshake captures
# - Probe floods
```

---

## 🏗️ Architecture

```
Darknet/
├── darknet/
│   ├── core/              # Core framework
│   │   ├── base.py        # Base classes for modules
│   │   ├── packet.py      # Packet handling
│   │   └── device.py      # Device management
│   ├── offensive/         # Red team modules
│   │   ├── deauth.py      # Deauth attacks
│   │   ├── evil_twin.py   # Evil twin
│   │   ├── pmkid.py       # PMKID capture
│   │   ├── handshake.py   # Handshake capture
│   │   ├── beacon_flood.py
│   │   └── auth_flood.py
│   ├── mitm/              # MITM modules
│   │   ├── arp_spoof.py   # ARP spoofing
│   │   ├── dns_spoof.py   # DNS spoofing
│   │   └── sniffer.py     # Packet sniffing
│   ├── defensive/         # Blue team modules
│   │   ├── ids.py         # Wireless IDS
│   │   └── monitor.py     # Network monitoring
│   ├── network/           # Network utilities
│   │   ├── scanner.py     # Network scanners
│   │   └── interface.py   # Interface management
│   ├── utils/             # Utilities
│   │   ├── constants.py   # Constants
│   │   ├── helpers.py     # Helper functions
│   │   └── logger.py      # Logging system
│   ├── config.py          # Configuration
│   └── cli.py             # CLI interface
├── tests/                 # Test suite
├── examples/              # Example scripts
├── docs/                  # Documentation
└── README.md
```

---

## 🔧 Configuration

### Interface Configuration
```python
from darknet.network.interface import InterfaceManager

mgr = InterfaceManager()
mgr.configure_for_attacks('wlan0', random_mac=True)
```

### Custom Attack Configuration
```python
from darknet.offensive.deauth import DeauthAttack

attack = DeauthAttack()
attack.setup(
    interface='wlan0',
    ap_mac='00:11:22:33:44:55',
    packet_count=500,
    injection_rate=200,
    reason_code=7
)
attack.run()
```

---

## 🎨 Matrix Theme

Darknet features a Matrix-inspired interface with:
- Green-on-black terminal output
- Rich formatted tables and panels
- Real-time packet visualizations
- ASCII art banners
- Color-coded severity levels

---

## 📊 Output Formats

### Captured Handshakes
- `.cap` - Standard pcap format (for aircrack-ng)
- `.hccapx` - Hashcat format

### PMKID Captures
- `.16800` - Hashcat mode 16800 format

### Logs
- Timestamped log files in `logs/`
- Rich console output with colors
- CSV export for analysis

---

## 🛡️ Defensive Best Practices

When using the IDS:
1. Monitor on a separate interface from attacks
2. Set appropriate thresholds for your environment
3. Log all alerts for forensic analysis
4. Correlate alerts with known legitimate activity
5. Implement automated response actions (with caution)

---

## ⚡ Performance Tips

### For Maximum Attack Speed
- Use wireless adapters with good chipsets (Atheros, Ralink)
- Disable unnecessary network services
- Use `-r 200` for maximum injection rate
- Run on dedicated security testing machine

### For Reliable Detection
- Use monitor mode on a separate interface
- Keep IDS thresholds conservative initially
- Tune thresholds based on your environment
- Enable all detection modules

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Inspired by Metasploit, Bettercap, and Aircrack-ng
- Built with Scapy, Click, and Rich libraries
- Thanks to the security research community

---

## 📞 Support

For bugs, feature requests, or questions:
- Open an issue on GitHub
- Check documentation in `docs/`

---

## 🔐 Security Notice

This tool is powerful and should be used responsibly:
- Only test networks you own or have written permission to test
- Be aware of local laws regarding wireless security testing
- Use strong passwords for any APs you create
- Clean up after testing (restore monitor mode, etc.)
- Document all testing activities

---

## 🚨 Warning Signs You're Detected

- Clients aren't reconnecting after deauth
- Network admin is making changes during your test
- Your packets are being blocked
- AP is logging unusual activity

**If detected during authorized testing:** Document findings and report to client.

---

**Remember: With great power comes great responsibility. Use Darknet ethically and legally.**

---

*Darknet v1.0.0 - Advanced Wireless Security Framework*
