# Darknet Examples

This directory contains example scripts and demonstrations for the Darknet framework.

## Demo Scripts

### demo-modules.sh
Shows all available modules, features, and command examples.

```bash
./examples/demo-modules.sh
```

### demo-scan.sh
Demonstrates the network scanning module capabilities.

```bash
sudo ./examples/demo-scan.sh
```

## Example Use Cases

### 1. Network Discovery

```bash
# Discover hosts on local network
sudo darknet scan ping -r 192.168.1.0/24

# ARP scan for faster local discovery
sudo darknet arp scan -i eth0 -r 192.168.1.0/24
```

### 2. Port Scanning

```bash
# Scan common ports
sudo darknet scan ports -t 192.168.1.100 -p 1-1000

# Scan specific ports
sudo darknet scan ports -t 192.168.1.100 -p 80,443,8080

# Full port scan
sudo darknet scan ports -t 192.168.1.100 -p 1-65535
```

### 3. Service Detection

```bash
# Detect services on open ports
sudo darknet scan ports -t 192.168.1.100 --service-detect

# Grab service banners
sudo darknet scan service -t 192.168.1.100 -p 80
```

### 4. WiFi Security Testing

```bash
# Scan for WiFi networks
sudo darknet wifi scan -i wlan0

# Monitor specific channel
sudo darknet wifi scan -i wlan0 -c 6

# Capture WPA handshake
sudo darknet wifi handshake -i wlan0 -b AA:BB:CC:DD:EE:FF -o capture.pcap
```

### 5. ARP Operations

```bash
# Scan network via ARP
sudo darknet arp scan -i eth0 -r 192.168.1.0/24

# View ARP cache
sudo darknet arp cache

# MITM attack (authorized testing only!)
sudo darknet arp mitm -i eth0 -t 192.168.1.100 -g 192.168.1.1
```

### 6. Stress Testing

```bash
# TCP SYN flood (authorized testing only!)
sudo darknet stress syn -t 192.168.1.100 -p 80 -d 60 -r 1000

# UDP flood
sudo darknet stress udp -t 192.168.1.100 -p 53 -d 30

# HTTP stress test
sudo darknet stress http -u http://192.168.1.100 -c 100
```

### 7. Packet Operations

```bash
# Craft TCP packet
sudo darknet packet craft --tcp --src 192.168.1.50 --dst 192.168.1.100

# Sniff packets
sudo darknet packet sniff -i eth0 -f "tcp port 80"

# Inject packet from file
sudo darknet packet inject -i eth0 -f packet.pcap
```

## Testing Lab Setup

For safe testing, set up an isolated lab:

### Virtual Lab Setup

1. **Use Virtual Machines:**
   - VirtualBox or VMware
   - Create isolated network
   - Use multiple VMs as targets

2. **Network Configuration:**
   ```bash
   # Create isolated network
   # VirtualBox: Host-Only Network
   # VMware: Custom Network (VMnet)
   ```

3. **Test Safely:**
   - No internet connection for lab network
   - Only test on your own VMs
   - Document all testing

### Physical Lab Setup

1. **Hardware:**
   - Dedicated switch/router
   - Multiple test machines
   - Wireless access point (for WiFi testing)

2. **Network Isolation:**
   - Separate from production network
   - No WAN connection
   - VLAN isolation if needed

3. **Test Targets:**
   - Old laptops/PCs
   - Raspberry Pi devices
   - IoT devices
   - Wireless access points

## Practice Scenarios

### Scenario 1: Network Reconnaissance
**Goal:** Map an entire network

```bash
# 1. Discover live hosts
sudo darknet scan ping -r 192.168.1.0/24

# 2. Scan for open ports
sudo darknet scan ports -t <discovered_host>

# 3. Identify services
sudo darknet scan service -t <discovered_host>

# 4. OS detection
sudo darknet scan os -t <discovered_host>
```

### Scenario 2: WiFi Assessment
**Goal:** Assess WiFi security

```bash
# 1. Scan for networks
sudo darknet wifi scan -i wlan0

# 2. Identify clients
sudo darknet wifi clients -i wlan0 -b <bssid>

# 3. Test deauth resistance
sudo darknet wifi deauth -i wlan0 -b <bssid> -c 10

# 4. Capture handshake
sudo darknet wifi handshake -i wlan0 -b <bssid>
```

### Scenario 3: MITM Testing
**Goal:** Test network segmentation

```bash
# 1. Position between targets
sudo darknet arp mitm -i eth0 -t 192.168.1.100 -g 192.168.1.1

# 2. Intercept traffic
sudo darknet packet sniff -i eth0 -f "host 192.168.1.100"

# 3. Analyze captured data
# (Use separate analysis tools)

# 4. Restore network
sudo darknet arp restore -i eth0 -t 192.168.1.100
```

## Important Notes

### Legal Requirements
- ✅ Get written authorization
- ✅ Define scope clearly
- ✅ Document everything
- ✅ Report findings responsibly
- ❌ Never test without permission

### Ethical Guidelines
1. Always obtain explicit permission
2. Stay within defined scope
3. Minimize impact on systems
4. Protect discovered data
5. Report vulnerabilities responsibly

### Best Practices
- Test in isolated labs first
- Start with passive reconnaissance
- Gradually increase intensity
- Monitor for unintended effects
- Have rollback procedures ready
- Document all actions
- Coordinate with stakeholders

## Additional Resources

### Learning Platforms
- **HackTheBox** - Hands-on hacking labs
- **TryHackMe** - Guided pentesting challenges
- **VulnHub** - Vulnerable VMs for practice
- **PentesterLab** - Web security exercises

### Certifications
- **CEH** - Certified Ethical Hacker
- **OSCP** - Offensive Security Certified Professional
- **GPEN** - GIAC Penetration Tester
- **eWPT** - eLearnSecurity Web Pentester

### Tools to Learn Alongside
- **Nmap** - Network scanner
- **Wireshark** - Packet analyzer
- **Metasploit** - Exploitation framework
- **Burp Suite** - Web app testing
- **Aircrack-ng** - WiFi security

## Troubleshooting Examples

If examples don't work:

```bash
# Check if darknet is installed
which darknet

# Run from build directory
cd /path/to/Darknet
sudo ./bin/darknet <command>

# Check permissions
sudo darknet <command>

# Verify network interfaces
ip link show
iwconfig  # For wireless
```

## Contributing Examples

Have a useful example? Contribute it!

1. Create your example script
2. Document it clearly
3. Test thoroughly
4. Submit a pull request

---

**Remember:** With great power comes great responsibility. Use Darknet ethically and legally!
