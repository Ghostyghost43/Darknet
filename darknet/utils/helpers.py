"""
Helper utilities for Darknet framework
"""

import os
import re
import subprocess
import time
from typing import List, Optional, Tuple
from netaddr import EUI, OUI
import psutil


def is_root() -> bool:
    """Check if running with root privileges"""
    return os.geteuid() == 0


def get_wireless_interfaces() -> List[str]:
    """Get list of wireless interfaces"""
    interfaces = []
    try:
        for iface in os.listdir('/sys/class/net/'):
            if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                interfaces.append(iface)
    except Exception:
        pass
    return interfaces


def get_interface_mode(interface: str) -> Optional[str]:
    """Get current mode of wireless interface"""
    try:
        result = subprocess.run(
            ['iwconfig', interface],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'Mode:Monitor' in result.stdout:
            return 'monitor'
        elif 'Mode:Managed' in result.stdout:
            return 'managed'
        elif 'Mode:Master' in result.stdout:
            return 'master'
    except Exception:
        pass
    return None


def set_monitor_mode(interface: str) -> Tuple[bool, str]:
    """
    Enable monitor mode on wireless interface
    Returns: (success, message)
    """
    try:
        # Check if already in monitor mode
        current_mode = get_interface_mode(interface)
        if current_mode == 'monitor':
            return True, f"{interface} is already in monitor mode"

        # Bring interface down
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True, timeout=5)

        # Kill interfering processes
        subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True, timeout=10)

        # Set monitor mode
        subprocess.run(['iw', interface, 'set', 'monitor', 'none'], check=True, timeout=5)

        # Bring interface up
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True, timeout=5)

        return True, f"Successfully enabled monitor mode on {interface}"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to enable monitor mode: {str(e)}"
    except subprocess.TimeoutExpired:
        return False, "Operation timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"


def set_managed_mode(interface: str) -> Tuple[bool, str]:
    """
    Disable monitor mode and return to managed mode
    Returns: (success, message)
    """
    try:
        # Bring interface down
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True, timeout=5)

        # Set managed mode
        subprocess.run(['iw', interface, 'set', 'type', 'managed'], check=True, timeout=5)

        # Bring interface up
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True, timeout=5)

        # Restart NetworkManager
        subprocess.run(['systemctl', 'restart', 'NetworkManager'], capture_output=True, timeout=10)

        return True, f"Successfully restored {interface} to managed mode"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to restore managed mode: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def change_mac(interface: str, new_mac: Optional[str] = None) -> Tuple[bool, str]:
    """
    Change MAC address of interface
    If new_mac is None, generates a random MAC
    Returns: (success, message)
    """
    try:
        if new_mac is None:
            # Generate random MAC address
            import random
            new_mac = "02:%02x:%02x:%02x:%02x:%02x" % (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )

        # Bring interface down
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True, timeout=5)

        # Change MAC
        subprocess.run(['ip', 'link', 'set', interface, 'address', new_mac], check=True, timeout=5)

        # Bring interface up
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True, timeout=5)

        return True, f"Successfully changed MAC address to {new_mac}"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to change MAC address: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def set_channel(interface: str, channel: int) -> Tuple[bool, str]:
    """
    Set channel for wireless interface
    Returns: (success, message)
    """
    try:
        subprocess.run(
            ['iw', 'dev', interface, 'set', 'channel', str(channel)],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True, f"Successfully set channel to {channel}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to set channel: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_current_channel(interface: str) -> Optional[int]:
    """Get current channel of interface"""
    try:
        result = subprocess.run(
            ['iw', 'dev', interface, 'info'],
            capture_output=True,
            text=True,
            timeout=5
        )
        match = re.search(r'channel (\d+)', result.stdout)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def get_mac_vendor(mac: str) -> str:
    """Get vendor name from MAC address"""
    try:
        mac_obj = EUI(mac)
        oui = mac_obj.oui
        return oui.registration().org
    except Exception:
        return "Unknown"


def validate_mac(mac: str) -> bool:
    """Validate MAC address format"""
    pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return bool(pattern.match(mac))


def validate_ssid(ssid: str) -> bool:
    """Validate SSID (0-32 bytes)"""
    return 0 <= len(ssid.encode('utf-8')) <= 32


def check_monitor_mode_support(interface: str) -> bool:
    """Check if interface supports monitor mode"""
    try:
        result = subprocess.run(
            ['iw', interface, 'info'],
            capture_output=True,
            text=True,
            timeout=5
        )
        result2 = subprocess.run(
            ['iw', 'phy'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'monitor' in result2.stdout.lower()
    except Exception:
        return False


def check_injection_support(interface: str) -> bool:
    """Check if interface supports packet injection"""
    try:
        # Try to inject a test packet
        result = subprocess.run(
            ['aireplay-ng', '--test', interface],
            capture_output=True,
            text=True,
            timeout=10
        )
        return 'Injection is working' in result.stdout
    except Exception:
        return False


def kill_network_managers():
    """Kill network managers that might interfere"""
    managers = ['NetworkManager', 'wpa_supplicant', 'dhclient']
    killed = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in managers:
                proc.kill()
                killed.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return killed


def get_interface_mac(interface: str) -> Optional[str]:
    """Get MAC address of interface"""
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            return f.read().strip()
    except Exception:
        return None


def check_dependencies() -> List[str]:
    """Check if required system dependencies are installed"""
    dependencies = [
        'airmon-ng',
        'airodump-ng',
        'aireplay-ng',
        'iw',
        'iwconfig',
        'ip',
        'tcpdump'
    ]

    missing = []
    for dep in dependencies:
        try:
            subprocess.run(['which', dep], capture_output=True, check=True, timeout=5)
        except subprocess.CalledProcessError:
            missing.append(dep)

    return missing


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_speed(speed: float) -> str:
    """Format speed in Mbps"""
    if speed >= 1000:
        return f"{speed/1000:.1f} Gbps"
    return f"{speed:.1f} Mbps"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    return re.sub(r'[^\w\-_\. ]', '_', filename)
