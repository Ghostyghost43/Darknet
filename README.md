# Darknet

**Network Pentesting & Stress Testing Framework**

A comprehensive C-based framework for network security testing, penetration testing, and stress testing. Designed for security professionals, researchers, and authorized testing engagements.

```
██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║
██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝
```

## ⚠️ LEGAL WARNING

**READ THIS CAREFULLY BEFORE USING THIS TOOL**

This software is intended for **AUTHORIZED SECURITY TESTING ONLY**.

- You MUST have explicit written permission to test any network, system, or device
- Unauthorized access to computer systems is **ILLEGAL** in virtually all jurisdictions
- Violators may face criminal prosecution, fines, and imprisonment
- This tool should only be used in:
  - Authorized penetration testing engagements
  - Your own isolated lab environments
  - Educational settings with proper authorization
  - CTF competitions and security challenges
  - Security research with proper ethical guidelines

**The authors and contributors assume NO LIABILITY for misuse of this software.**

By using this tool, you agree to use it responsibly and legally. If you disagree, DO NOT USE THIS SOFTWARE.

## 🎯 Features

### WiFi Attacks
- **Deauthentication Attacks** - Disconnect clients from access points
- **Evil Twin / Rogue AP** - Create fake access points
- **WPA/WPA2 Handshake Capture** - Capture authentication handshakes
- **WPS Attacks** - Pixie Dust and PIN bruteforce
- **Beacon Flooding** - Generate fake WiFi networks
- **Client Detection** - Monitor and enumerate WiFi clients

### Network Scanning
- **Host Discovery** - Ping sweeps and ARP scans
- **Port Scanning** - TCP (Connect, SYN, FIN, Xmas, NULL) and UDP scans
- **Service Detection** - Identify running services and versions
- **Banner Grabbing** - Extract service banners
- **OS Fingerprinting** - Detect target operating systems
- **Vulnerability Detection** - Identify common vulnerabilities
- **Network Mapping** - Comprehensive network topology discovery
- **Traceroute** - Path discovery and latency analysis

### ARP Attacks
- **ARP Cache Poisoning** - Manipulate ARP tables
- **Man-in-the-Middle (MITM)** - Intercept network traffic
- **Gateway Spoofing** - Impersonate network gateway
- **Bidirectional Poisoning** - Poison both directions of communication
- **Traffic Interception** - Capture and analyze intercepted packets
- **ARP Scanning** - Network discovery via ARP

### Stress Testing
- **TCP Floods** - SYN, ACK, RST, FIN flood attacks
- **UDP Floods** - UDP-based stress testing
- **ICMP Floods** - Ping floods and Ping of Death
- **HTTP Floods** - Application layer stress testing
- **Slowloris** - Slow HTTP attacks
- **DNS/NTP Amplification** - Reflection attacks
- **Fragmentation Attacks** - IP fragment-based attacks
- **Connection Exhaustion** - Resource depletion testing
- **Bandwidth Testing** - Network capacity testing

### Packet Crafting
- **Raw Packet Creation** - Build custom packets from scratch
- **Protocol Support** - Ethernet, IP, TCP, UDP, ICMP, ARP, DNS, HTTP
- **Packet Injection** - Send crafted packets to the network
- **Packet Sniffing** - Capture and analyze network traffic
- **PCAP Support** - Read and write capture files
- **Checksum Calculation** - Automatic protocol checksums
- **Packet Parsing** - Extract headers and payload data

## 📋 Requirements

### Build Dependencies
- GCC compiler (gcc >= 7.0)
- GNU Make
- libpcap-dev (for packet capture)
- pthread (POSIX threads)
- Standard C library

### Runtime Requirements
- Linux kernel 3.x or higher
- Root privileges (required for raw socket access)
- Network interface(s) for testing

### Optional
- Wireless network adapter with monitor mode support (for WiFi attacks)
- Multiple network interfaces (for advanced MITM scenarios)

## 🔧 Installation

### Clone the Repository
```bash
git clone https://github.com/codypratt88/Darknet.git
cd Darknet
```

### Install Dependencies (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install build-essential libpcap-dev
```

### Install Dependencies (Red Hat/CentOS/Fedora)
```bash
sudo yum install gcc make libpcap-devel
# or on newer systems:
sudo dnf install gcc make libpcap-devel
```

### Build the Framework
```bash
make
```

### Build Options
- `make debug` - Build with debug symbols
- `make release` - Build optimized release version
- `make clean` - Remove build artifacts
- `make install` - Install to /usr/local/bin (requires root)
- `make uninstall` - Remove from system

## 🚀 Usage

### Basic Command Structure
```bash
sudo darknet <module> <subcommand> [options]
```

**Note:** Darknet requires root privileges for raw socket access.

### Getting Help
```bash
darknet help              # General help
darknet modules           # List all modules
darknet <module> --help   # Module-specific help
```

## 📚 Documentation

- **README.md** - This file (overview and quick start)
- **ETHICAL_GUIDELINES.md** - Ethical use guidelines
- **LICENSE** - Legal license and terms
- **examples/** - Example usage scripts and scenarios

## 🔒 Security Best Practices

### For Testers
1. **Always get written authorization** before testing
2. **Document your scope** - Know what you can and cannot test
3. **Use isolated environments** for learning and development
4. **Log all activities** for accountability
5. **Clean up after testing** - Restore systems to original state
6. **Report findings responsibly** following disclosure guidelines

### For Defenders
1. **Monitor for ARP spoofing** - Use static ARP entries or detection tools
2. **Implement 802.1X** - Strong WiFi authentication
3. **Use WPA3** - Latest WiFi security standard
4. **Deploy IDS/IPS** - Detect and prevent attacks
5. **Rate limiting** - Protect against floods
6. **Network segmentation** - Limit attack surface

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" errors:**
- Solution: Run with sudo/root privileges

**"Interface not found":**
- Solution: Check interface name with `ip link` or `ifconfig`

**Build errors:**
- Solution: Ensure all dependencies are installed
- Try: `make clean && make`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## 📞 Contact & Support

- **Issues:** GitHub issue tracker
- **Security:** Report security issues privately

## 📊 Project Status

- **Version:** 1.0.0
- **Status:** Framework Complete - Implementation Stubs Ready
- **Development:** Active

### Current State

The framework is architecturally complete with all module interfaces defined. Core functionality is implemented at the skeleton level. To make it fully functional, you would need to:

1. **WiFi Module** - Integrate with nl80211/libnl for wireless operations
2. **Packet Module** - Complete libpcap integration for capture/injection
3. **Scanning Module** - Implement actual scanning algorithms
4. **Attack Modules** - Complete packet crafting and injection logic

The framework provides a solid foundation for building out each module with real implementations.

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
