"""
Network interface management module
"""

from darknet.utils.helpers import *
from darknet.utils.logger import setup_logger
from typing import List, Optional, Tuple
import subprocess
import time


class InterfaceManager:
    """
    Manage network interfaces
    Configure monitor mode, change MAC, set channels, etc.
    """

    def __init__(self):
        self.logger = setup_logger("InterfaceManager")
        self.original_mac = {}
        self.original_mode = {}

    def list_interfaces(self) -> List[str]:
        """List all wireless interfaces"""
        interfaces = get_wireless_interfaces()
        self.logger.info(f"Found {len(interfaces)} wireless interfaces: {', '.join(interfaces)}")
        return interfaces

    def get_interface_info(self, interface: str) -> dict:
        """Get detailed interface information"""
        try:
            info = {
                'interface': interface,
                'mode': get_interface_mode(interface),
                'mac': get_interface_mac(interface),
                'channel': get_current_channel(interface),
                'monitor_support': check_monitor_mode_support(interface),
                'injection_support': check_injection_support(interface)
            }

            self.logger.info(f"Interface {interface}:")
            for key, value in info.items():
                if key != 'interface':
                    self.logger.info(f"  {key}: {value}")

            return info

        except Exception as e:
            self.logger.error(f"Failed to get interface info: {e}")
            return {}

    def enable_monitor_mode(self, interface: str, save_original: bool = True) -> bool:
        """
        Enable monitor mode on interface
        Args:
            interface: Interface name
            save_original: Save original mode for restoration
        """
        try:
            if save_original:
                self.original_mode[interface] = get_interface_mode(interface)
                self.original_mac[interface] = get_interface_mac(interface)

            success, message = set_monitor_mode(interface)

            if success:
                self.logger.success(message)

                # Verify monitor mode
                time.sleep(1)
                mode = get_interface_mode(interface)
                if mode != 'monitor':
                    self.logger.warning(f"Interface mode is {mode}, not monitor")
                    return False

                # Check injection support
                if check_injection_support(interface):
                    self.logger.success(f"Packet injection is working on {interface}")
                else:
                    self.logger.warning(f"Packet injection may not work on {interface}")

                return True
            else:
                self.logger.error(message)
                return False

        except Exception as e:
            self.logger.error(f"Failed to enable monitor mode: {e}")
            return False

    def disable_monitor_mode(self, interface: str, restore_original: bool = True) -> bool:
        """
        Disable monitor mode and restore managed mode
        Args:
            interface: Interface name
            restore_original: Restore original MAC address
        """
        try:
            success, message = set_managed_mode(interface)

            if success:
                self.logger.success(message)

                # Restore original MAC if saved
                if restore_original and interface in self.original_mac:
                    original_mac = self.original_mac[interface]
                    self.change_mac(interface, original_mac)

                return True
            else:
                self.logger.error(message)
                return False

        except Exception as e:
            self.logger.error(f"Failed to disable monitor mode: {e}")
            return False

    def change_mac(self, interface: str, new_mac: Optional[str] = None) -> bool:
        """
        Change MAC address
        Args:
            interface: Interface name
            new_mac: New MAC address (None for random)
        """
        try:
            # Save original MAC if not saved
            if interface not in self.original_mac:
                self.original_mac[interface] = get_interface_mac(interface)

            success, message = change_mac(interface, new_mac)

            if success:
                self.logger.success(message)
                return True
            else:
                self.logger.error(message)
                return False

        except Exception as e:
            self.logger.error(f"Failed to change MAC: {e}")
            return False

    def set_channel(self, interface: str, channel: int) -> bool:
        """
        Set wireless channel
        Args:
            interface: Interface name
            channel: Channel number
        """
        try:
            success, message = set_channel(interface, channel)

            if success:
                self.logger.success(message)
                return True
            else:
                self.logger.error(message)
                return False

        except Exception as e:
            self.logger.error(f"Failed to set channel: {e}")
            return False

    def get_current_channel(self, interface: str) -> Optional[int]:
        """Get current channel"""
        return get_current_channel(interface)

    def kill_interfering_processes(self) -> List[str]:
        """Kill processes that might interfere with wireless operations"""
        try:
            killed = kill_network_managers()

            if killed:
                self.logger.info(f"Killed interfering processes: {', '.join(killed)}")
            else:
                self.logger.info("No interfering processes found")

            return killed

        except Exception as e:
            self.logger.error(f"Failed to kill processes: {e}")
            return []

    def check_dependencies(self) -> bool:
        """Check if required system dependencies are installed"""
        missing = check_dependencies()

        if missing:
            self.logger.error(f"Missing dependencies: {', '.join(missing)}")
            self.logger.info("Install with: apt-get install " + ' '.join(missing))
            return False
        else:
            self.logger.success("All dependencies are installed")
            return True

    def restore_interface(self, interface: str) -> bool:
        """
        Restore interface to original state
        Args:
            interface: Interface name
        """
        try:
            self.logger.info(f"Restoring interface {interface} to original state")

            # Restore managed mode
            if interface in self.original_mode:
                if self.original_mode[interface] == 'managed':
                    self.disable_monitor_mode(interface, restore_original=True)

            # Restore MAC
            if interface in self.original_mac:
                self.change_mac(interface, self.original_mac[interface])

            self.logger.success(f"Interface {interface} restored")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restore interface: {e}")
            return False

    def configure_for_attacks(self, interface: str, random_mac: bool = True) -> bool:
        """
        Configure interface for wireless attacks
        Args:
            interface: Interface name
            random_mac: Use random MAC address
        """
        try:
            self.logger.info(f"Configuring {interface} for wireless attacks")

            # Check dependencies
            if not self.check_dependencies():
                return False

            # Kill interfering processes
            self.kill_interfering_processes()

            # Change MAC if requested
            if random_mac:
                self.change_mac(interface)

            # Enable monitor mode
            if not self.enable_monitor_mode(interface):
                return False

            self.logger.success(f"Interface {interface} configured and ready for attacks")
            return True

        except Exception as e:
            self.logger.error(f"Failed to configure interface: {e}")
            return False

    def start_ap(self, interface: str, ssid: str, channel: int = 6, password: Optional[str] = None) -> bool:
        """
        Start a software access point
        Args:
            interface: Interface name
            ssid: AP SSID
            channel: Channel
            password: WPA2 password (None for open)
        """
        try:
            self.logger.info(f"Starting AP: {ssid} on channel {channel}")

            # Create hostapd config
            config = f"""
interface={interface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
macaddr_acl=0
ignore_broadcast_ssid=0
"""

            if password:
                config += f"""
auth_algs=1
wpa=2
wpa_passphrase={password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
"""
            else:
                config += "auth_algs=1\n"

            # Write config
            config_file = f'/tmp/darknet_ap_{interface}.conf'
            with open(config_file, 'w') as f:
                f.write(config)

            # Start hostapd
            proc = subprocess.Popen(
                ['hostapd', config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.logger.success(f"AP started: {ssid}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start AP: {e}")
            return False

    def stop_ap(self, interface: str) -> bool:
        """Stop software access point"""
        try:
            subprocess.run(['pkill', 'hostapd'], capture_output=True)
            config_file = f'/tmp/darknet_ap_{interface}.conf'
            if os.path.exists(config_file):
                os.remove(config_file)
            self.logger.info("AP stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop AP: {e}")
            return False
