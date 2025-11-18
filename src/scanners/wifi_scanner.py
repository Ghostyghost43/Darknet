"""
WiFi scanner module for detecting nearby WiFi devices and access points.
Optimized for Linux/Kali on Raspberry Pi.
"""
import os
import re
import subprocess
from typing import List, Dict, Optional
from datetime import datetime

try:
    from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class WiFiScanner:
    """Scan for WiFi devices and access points."""

    def __init__(self, interface: str = None):
        """
        Initialize WiFi scanner.

        Args:
            interface: WiFi interface to use (e.g., wlan0, wlan0mon)
        """
        self.interface = interface or self._find_wifi_interface()
        self.detected_devices = {}
        self.oui_db = self._load_oui_database()

    def _find_wifi_interface(self) -> str:
        """Find available WiFi interface."""
        try:
            result = subprocess.run(
                ['iwconfig'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line or 'ESSID' in line:
                    interface = line.split()[0]
                    return interface

            # Fallback: check /sys/class/net
            net_path = '/sys/class/net'
            if os.path.exists(net_path):
                for iface in os.listdir(net_path):
                    wireless_path = f'{net_path}/{iface}/wireless'
                    if os.path.exists(wireless_path):
                        return iface
        except Exception as e:
            print(f"Warning: Could not auto-detect WiFi interface: {e}")

        return 'wlan0'  # Default fallback

    def _load_oui_database(self) -> Dict[str, str]:
        """Load OUI (vendor) database for MAC address lookup."""
        # Simplified OUI database - common surveillance/tracking device vendors
        return {
            '00:0C:43': 'Ralink Technology',
            '00:13:EF': 'Intel',
            '00:1B:63': 'Apple',
            '00:50:F2': 'Microsoft',
            '08:00:27': 'VirtualBox',
            '08:00:28': 'Texas Instruments',
            '24:6F:28': 'Raspberry Pi Trading',
            'B8:27:EB': 'Raspberry Pi Foundation',
            'DC:A6:32': 'Raspberry Pi Trading',
            'E4:5F:01': 'Raspberry Pi Trading',
        }

    def get_vendor(self, mac: str) -> Optional[str]:
        """Get vendor from MAC address using OUI."""
        if not mac:
            return None

        oui = mac[:8].upper()
        vendor = self.oui_db.get(oui)

        if not vendor:
            # Try to use system OUI database if available
            try:
                result = subprocess.run(
                    ['grep', '-i', oui, '/usr/share/ieee-data/oui.txt'],
                    capture_output=True, text=True, timeout=2
                )
                if result.stdout:
                    vendor = result.stdout.split('\t')[-1].strip()
            except:
                pass

        return vendor or 'Unknown'

    def enable_monitor_mode(self) -> bool:
        """Enable monitor mode on WiFi interface."""
        try:
            # Check if already in monitor mode
            if 'mon' in self.interface:
                return True

            print(f"Attempting to enable monitor mode on {self.interface}...")

            # Method 1: Using airmon-ng (if available)
            if self._command_exists('airmon-ng'):
                subprocess.run(
                    ['airmon-ng', 'start', self.interface],
                    capture_output=True, timeout=10
                )
                self.interface = f"{self.interface}mon"
                print(f"Monitor mode enabled: {self.interface}")
                return True

            # Method 2: Using iwconfig/ifconfig
            subprocess.run(['ifconfig', self.interface, 'down'], capture_output=True)
            subprocess.run(['iwconfig', self.interface, 'mode', 'monitor'], capture_output=True)
            subprocess.run(['ifconfig', self.interface, 'up'], capture_output=True)
            print(f"Monitor mode enabled: {self.interface}")
            return True

        except Exception as e:
            print(f"Warning: Could not enable monitor mode: {e}")
            print("Continuing with managed mode (limited functionality)")
            return False

    def disable_monitor_mode(self):
        """Disable monitor mode."""
        try:
            if 'mon' in self.interface:
                if self._command_exists('airmon-ng'):
                    subprocess.run(
                        ['airmon-ng', 'stop', self.interface],
                        capture_output=True, timeout=10
                    )
                else:
                    base_interface = self.interface.replace('mon', '')
                    subprocess.run(['ifconfig', base_interface, 'down'], capture_output=True)
                    subprocess.run(['iwconfig', base_interface, 'mode', 'managed'], capture_output=True)
                    subprocess.run(['ifconfig', base_interface, 'up'], capture_output=True)
        except Exception as e:
            print(f"Warning: Could not disable monitor mode: {e}")

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(
                ['which', command], capture_output=True, check=True
            )
            return True
        except:
            return False

    def scan_with_scapy(self, duration: int = 10) -> List[Dict]:
        """
        Scan for WiFi devices using scapy (requires monitor mode).

        Args:
            duration: Scan duration in seconds

        Returns:
            List of detected devices
        """
        if not SCAPY_AVAILABLE:
            raise ImportError("Scapy not available. Install with: pip install scapy")

        print(f"Scanning on {self.interface} for {duration} seconds...")
        devices = []

        def packet_handler(packet):
            if packet.haslayer(Dot11):
                # Get MAC address (transmitter address)
                mac = None
                if packet.addr2:
                    mac = packet.addr2.upper()

                if not mac or mac == 'FF:FF:FF:FF:FF:FF':
                    return

                # Determine device type
                device_type = 'STATION'
                ssid = None
                signal_strength = None

                # Access Point
                if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
                    device_type = 'ACCESS_POINT'
                    if packet.haslayer(Dot11Beacon):
                        ssid = packet[Dot11Beacon].info.decode('utf-8', errors='ignore')
                    elif packet.haslayer(Dot11ProbeResp):
                        ssid = packet[Dot11ProbeResp].info.decode('utf-8', errors='ignore')

                # Client/Station
                elif packet.haslayer(Dot11ProbeReq):
                    device_type = 'STATION'
                    ssid = packet[Dot11ProbeReq].info.decode('utf-8', errors='ignore')

                # Get signal strength
                if hasattr(packet, 'dBm_AntSignal'):
                    signal_strength = packet.dBm_AntSignal

                # Store device info
                if mac not in self.detected_devices:
                    vendor = self.get_vendor(mac)
                    device_info = {
                        'mac': mac,
                        'type': device_type,
                        'vendor': vendor,
                        'ssid': ssid,
                        'signal_strength': signal_strength,
                        'timestamp': datetime.now().isoformat(),
                        'channel': None
                    }
                    self.detected_devices[mac] = device_info
                    devices.append(device_info)
                    print(f"  [+] {device_type}: {mac} ({vendor}) - {ssid or 'Hidden'}")

        try:
            sniff(iface=self.interface, prn=packet_handler, timeout=duration, store=False)
        except Exception as e:
            print(f"Error during scapy scan: {e}")
            print("Make sure you have root privileges and monitor mode is enabled")

        return devices

    def scan_with_iwlist(self) -> List[Dict]:
        """
        Scan for WiFi networks using iwlist (fallback method).
        Less detailed but doesn't require monitor mode.
        """
        devices = []

        try:
            result = subprocess.run(
                ['iwlist', self.interface, 'scan'],
                capture_output=True, text=True, timeout=30
            )

            current_device = None

            for line in result.stdout.split('\n'):
                line = line.strip()

                # New cell/device
                if 'Address:' in line and 'Cell' in line:
                    if current_device:
                        devices.append(current_device)

                    mac = line.split('Address: ')[-1].strip().upper()
                    vendor = self.get_vendor(mac)

                    current_device = {
                        'mac': mac,
                        'type': 'ACCESS_POINT',
                        'vendor': vendor,
                        'ssid': None,
                        'signal_strength': None,
                        'timestamp': datetime.now().isoformat(),
                        'channel': None,
                        'encryption': None
                    }

                elif current_device:
                    if 'ESSID:' in line:
                        ssid = line.split('ESSID:')[-1].strip().strip('"')
                        current_device['ssid'] = ssid if ssid else 'Hidden'

                    elif 'Channel:' in line:
                        try:
                            channel = int(line.split('Channel:')[-1].strip())
                            current_device['channel'] = channel
                        except:
                            pass

                    elif 'Signal level=' in line:
                        try:
                            signal = line.split('Signal level=')[-1].split()[0]
                            current_device['signal_strength'] = int(signal)
                        except:
                            pass

                    elif 'Encryption key:' in line:
                        encryption = 'on' in line.lower()
                        current_device['encryption'] = 'Encrypted' if encryption else 'Open'

            if current_device:
                devices.append(current_device)

            for device in devices:
                mac = device['mac']
                if mac not in self.detected_devices:
                    self.detected_devices[mac] = device
                    print(f"  [+] AP: {mac} ({device['vendor']}) - {device['ssid']}")

        except subprocess.TimeoutExpired:
            print("Warning: iwlist scan timed out")
        except Exception as e:
            print(f"Error during iwlist scan: {e}")

        return devices

    def scan(self, method: str = 'auto', duration: int = 10) -> List[Dict]:
        """
        Scan for WiFi devices.

        Args:
            method: Scan method ('scapy', 'iwlist', or 'auto')
            duration: Scan duration in seconds (for scapy)

        Returns:
            List of detected devices
        """
        devices = []

        if method == 'auto':
            if SCAPY_AVAILABLE and os.geteuid() == 0:
                method = 'scapy'
            else:
                method = 'iwlist'

        if method == 'scapy':
            if not SCAPY_AVAILABLE:
                print("Scapy not available, falling back to iwlist")
                method = 'iwlist'
            elif os.geteuid() != 0:
                print("Root privileges required for scapy, falling back to iwlist")
                method = 'iwlist'

        if method == 'scapy':
            devices = self.scan_with_scapy(duration)
        elif method == 'iwlist':
            devices = self.scan_with_iwlist()

        return devices

    def get_detected_devices(self) -> Dict:
        """Get all detected devices."""
        return self.detected_devices

    def clear_devices(self):
        """Clear detected devices list."""
        self.detected_devices = {}
