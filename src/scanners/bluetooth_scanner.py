"""
Bluetooth scanner module for detecting nearby Bluetooth devices.
Detects phones, trackers (AirTags, Tiles), and other BT devices.
Optimized for Linux/Kali on Raspberry Pi.
"""
import os
import re
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
import time


class BluetoothScanner:
    """Scan for Bluetooth and BLE devices."""

    def __init__(self, adapter: str = 'hci0'):
        """
        Initialize Bluetooth scanner.

        Args:
            adapter: Bluetooth adapter to use (e.g., hci0)
        """
        self.adapter = adapter
        self.detected_devices = {}
        self.tracking_device_indicators = {
            'AirTag', 'Tile', 'Galaxy SmartTag', 'Chipolo',
            'Tracker', 'Find My', 'TrackR'
        }

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(
                ['which', command], capture_output=True, check=True
            )
            return True
        except:
            return False

    def check_bluetooth_available(self) -> bool:
        """Check if Bluetooth is available and adapter is up."""
        try:
            result = subprocess.run(
                ['hciconfig', self.adapter],
                capture_output=True, text=True, timeout=5
            )
            if 'UP RUNNING' in result.stdout:
                return True
            else:
                # Try to bring it up
                subprocess.run(
                    ['hciconfig', self.adapter, 'up'],
                    capture_output=True, timeout=5
                )
                return True
        except Exception as e:
            print(f"Warning: Bluetooth adapter issue: {e}")
            return False

    def identify_device_type(self, device_class: str, name: str) -> str:
        """
        Identify if device is potentially a tracking device.

        Returns: 'TRACKER', 'PHONE', 'COMPUTER', 'AUDIO', 'WEARABLE', 'UNKNOWN'
        """
        name_lower = name.lower() if name else ''

        # Check for known tracking devices
        for indicator in self.tracking_device_indicators:
            if indicator.lower() in name_lower:
                return 'TRACKER'

        # Analyze device class
        if device_class:
            # Phone indicators
            if '0x5a020c' in device_class or '0x7a020c' in device_class:
                return 'PHONE'
            # Computer indicators
            elif '0x100' in device_class or '0x10c' in device_class:
                return 'COMPUTER'
            # Audio device
            elif '0x240404' in device_class or '0x200000' in device_class:
                return 'AUDIO'
            # Wearable
            elif '0x1c' in device_class or 'wearable' in name_lower:
                return 'WEARABLE'

        # Check name patterns
        if any(x in name_lower for x in ['phone', 'iphone', 'galaxy', 'pixel', 'oneplus']):
            return 'PHONE'
        elif any(x in name_lower for x in ['macbook', 'laptop', 'pc', 'thinkpad']):
            return 'COMPUTER'
        elif any(x in name_lower for x in ['watch', 'band', 'fit']):
            return 'WEARABLE'
        elif any(x in name_lower for x in ['headphone', 'earbud', 'speaker', 'airpod']):
            return 'AUDIO'

        return 'UNKNOWN'

    def scan_with_hcitool(self, duration: int = 8) -> List[Dict]:
        """
        Scan for Bluetooth Classic devices using hcitool.

        Args:
            duration: Scan duration in seconds

        Returns:
            List of detected devices
        """
        devices = []

        if not self._command_exists('hcitool'):
            print("Warning: hcitool not found. Install bluez package.")
            return devices

        try:
            print(f"Scanning for Bluetooth Classic devices ({duration}s)...")

            # Perform inquiry scan
            result = subprocess.run(
                ['hcitool', '-i', self.adapter, 'scan', '--length={}'.format(duration)],
                capture_output=True, text=True, timeout=duration + 10
            )

            for line in result.stdout.split('\n'):
                # Skip header
                if 'Scanning' in line or not line.strip():
                    continue

                parts = line.strip().split(maxsplit=1)
                if len(parts) >= 1:
                    mac = parts[0].upper()
                    name = parts[1] if len(parts) > 1 else 'Unknown'

                    # Get additional info
                    device_class = self._get_device_class(mac)
                    rssi = self._get_rssi(mac)
                    device_type = self.identify_device_type(device_class, name)

                    device_info = {
                        'mac': mac,
                        'name': name,
                        'type': device_type,
                        'device_class': device_class,
                        'signal_strength': rssi,
                        'protocol': 'BT_CLASSIC',
                        'timestamp': datetime.now().isoformat(),
                        'is_tracker': device_type == 'TRACKER'
                    }

                    self.detected_devices[mac] = device_info
                    devices.append(device_info)

                    indicator = " [!!! TRACKER !!!]" if device_type == 'TRACKER' else ""
                    print(f"  [+] {device_type}: {mac} - {name}{indicator}")

        except subprocess.TimeoutExpired:
            print("Warning: Bluetooth scan timed out")
        except Exception as e:
            print(f"Error during hcitool scan: {e}")

        return devices

    def scan_with_bluetoothctl(self, duration: int = 10) -> List[Dict]:
        """
        Scan for BLE devices using bluetoothctl.
        Better for detecting modern trackers like AirTags.

        Args:
            duration: Scan duration in seconds

        Returns:
            List of detected devices
        """
        devices = []

        if not self._command_exists('bluetoothctl'):
            print("Warning: bluetoothctl not found. Install bluez package.")
            return devices

        try:
            print(f"Scanning for BLE devices ({duration}s)...")

            # Start bluetoothctl process
            process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send scan command
            process.stdin.write('scan on\n')
            process.stdin.flush()

            # Scan for specified duration
            time.sleep(duration)

            # Stop scan
            process.stdin.write('scan off\n')
            process.stdin.write('exit\n')
            process.stdin.flush()

            # Read output
            output, _ = process.communicate(timeout=5)

            # Parse output
            for line in output.split('\n'):
                if 'Device' in line and not 'removed' in line.lower():
                    # Format: [NEW/CHG] Device MAC_ADDRESS Name
                    parts = line.split()

                    if len(parts) >= 3:
                        mac = parts[2].upper()
                        name = ' '.join(parts[3:]) if len(parts) > 3 else 'Unknown'

                        # Get RSSI if available
                        rssi = None
                        if 'RSSI:' in line:
                            try:
                                rssi_match = re.search(r'RSSI:\s*(-?\d+)', line)
                                if rssi_match:
                                    rssi = int(rssi_match.group(1))
                            except:
                                pass

                        device_type = self.identify_device_type(None, name)

                        device_info = {
                            'mac': mac,
                            'name': name,
                            'type': device_type,
                            'device_class': None,
                            'signal_strength': rssi,
                            'protocol': 'BLE',
                            'timestamp': datetime.now().isoformat(),
                            'is_tracker': device_type == 'TRACKER'
                        }

                        if mac not in self.detected_devices:
                            self.detected_devices[mac] = device_info
                            devices.append(device_info)

                            indicator = " [!!! TRACKER !!!]" if device_type == 'TRACKER' else ""
                            print(f"  [+] {device_type}: {mac} - {name}{indicator}")

        except Exception as e:
            print(f"Error during bluetoothctl scan: {e}")
            try:
                process.kill()
            except:
                pass

        return devices

    def scan_with_lescan(self, duration: int = 10) -> List[Dict]:
        """
        Scan for BLE devices using hcitool lescan (alternative method).

        Args:
            duration: Scan duration in seconds

        Returns:
            List of detected devices
        """
        devices = []

        if not self._command_exists('hcitool'):
            return devices

        try:
            print(f"Scanning for BLE devices with lescan ({duration}s)...")

            # Start lescan
            process = subprocess.Popen(
                ['hcitool', '-i', self.adapter, 'lescan', '--duplicates'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Scan for duration
            time.sleep(duration)

            # Stop scan
            process.terminate()
            output, _ = process.communicate(timeout=5)

            # Parse output
            for line in output.split('\n'):
                if not line.strip() or 'LE Scan' in line:
                    continue

                parts = line.strip().split(maxsplit=1)
                if len(parts) >= 1:
                    mac = parts[0].upper()
                    name = parts[1] if len(parts) > 1 else 'Unknown'

                    if mac and mac not in self.detected_devices:
                        device_type = self.identify_device_type(None, name)

                        device_info = {
                            'mac': mac,
                            'name': name,
                            'type': device_type,
                            'device_class': None,
                            'signal_strength': None,
                            'protocol': 'BLE',
                            'timestamp': datetime.now().isoformat(),
                            'is_tracker': device_type == 'TRACKER'
                        }

                        self.detected_devices[mac] = device_info
                        devices.append(device_info)

                        indicator = " [!!! TRACKER !!!]" if device_type == 'TRACKER' else ""
                        print(f"  [+] {device_type}: {mac} - {name}{indicator}")

        except Exception as e:
            print(f"Error during lescan: {e}")
            try:
                process.kill()
            except:
                pass

        return devices

    def _get_device_class(self, mac: str) -> Optional[str]:
        """Get device class for a MAC address."""
        try:
            result = subprocess.run(
                ['hcitool', 'info', mac],
                capture_output=True, text=True, timeout=5
            )

            for line in result.stdout.split('\n'):
                if 'Class:' in line:
                    return line.split('Class:')[-1].strip()
        except:
            pass

        return None

    def _get_rssi(self, mac: str) -> Optional[int]:
        """Get RSSI (signal strength) for a device."""
        try:
            result = subprocess.run(
                ['hcitool', 'rssi', mac],
                capture_output=True, text=True, timeout=5
            )

            if 'RSSI return value:' in result.stdout:
                rssi_str = result.stdout.split('RSSI return value:')[-1].strip()
                return int(rssi_str)
        except:
            pass

        return None

    def scan(self, scan_types: List[str] = None, duration: int = 10) -> List[Dict]:
        """
        Comprehensive Bluetooth scan.

        Args:
            scan_types: List of scan types ('classic', 'ble', 'lescan') or None for all
            duration: Scan duration in seconds

        Returns:
            List of all detected devices
        """
        if not self.check_bluetooth_available():
            print("Error: Bluetooth not available")
            return []

        all_devices = []

        if scan_types is None:
            scan_types = ['classic', 'ble']

        if 'classic' in scan_types:
            devices = self.scan_with_hcitool(duration)
            all_devices.extend(devices)

        if 'ble' in scan_types:
            devices = self.scan_with_bluetoothctl(duration)
            all_devices.extend(devices)

        if 'lescan' in scan_types:
            devices = self.scan_with_lescan(duration)
            all_devices.extend(devices)

        return all_devices

    def get_detected_devices(self) -> Dict:
        """Get all detected devices."""
        return self.detected_devices

    def clear_devices(self):
        """Clear detected devices list."""
        self.detected_devices = {}

    def get_trackers(self) -> List[Dict]:
        """Get devices identified as trackers."""
        return [d for d in self.detected_devices.values() if d.get('is_tracker', False)]
