"""
Network and wireless scanning modules
"""

from scapy.all import *
from darknet.core.base import BaseModule
from darknet.core.packet import PacketHandler
from darknet.core.device import WirelessDevice, NetworkDevice, DeviceManager
from darknet.utils.constants import *
from darknet.utils.helpers import get_mac_vendor
from typing import List, Dict
import time
import subprocess
from datetime import datetime


class WirelessScanner(BaseModule):
    """
    Comprehensive wireless network scanner
    Discovers APs, clients, and captures network information
    """

    def __init__(self):
        super().__init__(
            name="Wireless Scanner",
            description="Scan for wireless networks and clients"
        )
        self.device_manager = DeviceManager()
        self.packet_handler = None
        self.channel_hop = True
        self.hop_interval = 0.5
        self.channels = WIFI_CHANNELS_2GHZ
        self.current_channel = 1
        self.scan_duration = 30
        self.hop_thread = None

    def setup(self, **kwargs) -> bool:
        """
        Setup wireless scanner
        Args:
            interface: Wireless interface in monitor mode
            channel_hop: Enable channel hopping
            hop_interval: Channel hop interval in seconds
            channels: List of channels to scan
            scan_duration: Scan duration in seconds
        """
        try:
            self.interface = kwargs.get('interface')
            self.channel_hop = kwargs.get('channel_hop', True)
            self.hop_interval = kwargs.get('hop_interval', 0.5)
            self.channels = kwargs.get('channels', WIFI_CHANNELS_2GHZ)
            self.scan_duration = kwargs.get('scan_duration', 30)

            if not self.interface:
                self.logger.error("Interface required")
                return False

            self.packet_handler = PacketHandler(self.interface)

            self.logger.info(f"Wireless scanner configured:")
            self.logger.info(f"  Interface: {self.interface}")
            self.logger.info(f"  Channel hop: {self.channel_hop}")
            self.logger.info(f"  Scan duration: {self.scan_duration}s")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _channel_hopper(self):
        """Hop through channels"""
        while not self._stop_event.is_set():
            try:
                self.current_channel = self.channels[self.channels.index(self.current_channel) + 1] \
                    if self.current_channel in self.channels[:-1] else self.channels[0]

                subprocess.run(
                    ['iw', 'dev', self.interface, 'set', 'channel', str(self.current_channel)],
                    capture_output=True,
                    timeout=2
                )

                time.sleep(self.hop_interval)

            except Exception as e:
                self.logger.debug(f"Channel hop error: {e}")

    def _process_packet(self, packet):
        """Process captured packet"""
        try:
            if not packet.haslayer(Dot11):
                return

            # Extract packet information
            pkt_type = packet.type
            pkt_subtype = packet.subtype

            # Beacon frame - Access Point
            if pkt_type == 0 and pkt_subtype == 8:
                self._process_beacon(packet)

            # Probe request - Client
            elif pkt_type == 0 and pkt_subtype == 4:
                self._process_probe_request(packet)

            # Probe response
            elif pkt_type == 0 and pkt_subtype == 5:
                self._process_probe_response(packet)

            # Data frame
            elif pkt_type == 2:
                self._process_data_frame(packet)

        except Exception as e:
            self.logger.debug(f"Error processing packet: {e}")

    def _process_beacon(self, packet):
        """Process beacon frame"""
        try:
            bssid = packet[Dot11].addr3
            ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore') if packet[Dot11Elt].info else ""

            # Get encryption
            encryption = PacketHandler.get_encryption_type(packet)

            # Get channel
            channel = PacketHandler.get_channel_from_packet(packet)

            # Get signal strength
            signal = PacketHandler.get_signal_strength(packet)

            # Get or create device
            device = self.device_manager.get_wireless_device(bssid)
            if device:
                device.update(
                    ssid=ssid,
                    encryption=encryption,
                    channel=channel,
                    signal_strength=signal or device.signal_strength,
                    beacons=device.beacons + 1,
                    packets=device.packets + 1
                )
            else:
                device = WirelessDevice(
                    mac=bssid,
                    ssid=ssid,
                    channel=channel,
                    encryption=encryption,
                    signal_strength=signal or -100,
                    vendor=get_mac_vendor(bssid),
                    device_type='ap',
                    beacons=1,
                    packets=1
                )
                self.device_manager.add_wireless_device(device)
                self.logger.info(f"New AP: {ssid or '<Hidden>'} ({bssid}) - {encryption} - Ch {channel}")

        except Exception as e:
            self.logger.debug(f"Error processing beacon: {e}")

    def _process_probe_request(self, packet):
        """Process probe request"""
        try:
            client_mac = packet[Dot11].addr2

            # Get SSID being probed
            ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore') if packet[Dot11Elt].info else ""

            # Get or create client device
            device = self.device_manager.get_wireless_device(client_mac)
            if device:
                if ssid and ssid not in device.probe_requests:
                    device.probe_requests.append(ssid)
                device.packets += 1
                device.last_seen = datetime.now()
            else:
                device = WirelessDevice(
                    mac=client_mac,
                    vendor=get_mac_vendor(client_mac),
                    device_type='client',
                    packets=1,
                    probe_requests=[ssid] if ssid else []
                )
                self.device_manager.add_wireless_device(device)
                self.logger.info(f"New client: {client_mac} probing for '{ssid}'")

        except Exception as e:
            self.logger.debug(f"Error processing probe request: {e}")

    def _process_probe_response(self, packet):
        """Process probe response"""
        try:
            bssid = packet[Dot11].addr3
            ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore') if packet[Dot11Elt].info else ""

            device = self.device_manager.get_wireless_device(bssid)
            if device:
                device.update(ssid=ssid, packets=device.packets + 1)

        except Exception as e:
            self.logger.debug(f"Error processing probe response: {e}")

    def _process_data_frame(self, packet):
        """Process data frame"""
        try:
            # Extract addresses
            addr1 = packet[Dot11].addr1
            addr2 = packet[Dot11].addr2
            addr3 = packet[Dot11].addr3

            # Update packet counts and associations
            for addr in [addr1, addr2, addr3]:
                if addr and addr != "ff:ff:ff:ff:ff:ff":
                    device = self.device_manager.get_wireless_device(addr)
                    if device:
                        device.packets += 1
                        device.data_packets += 1
                        device.last_seen = datetime.now()

                        # Try to determine client-AP association
                        if device.device_type == 'client' and addr3 and addr3 != addr:
                            device.associated_ap = addr3
                            ap = self.device_manager.get_wireless_device(addr3)
                            if ap and ap.device_type == 'ap':
                                ap.add_client(addr)

        except Exception as e:
            self.logger.debug(f"Error processing data frame: {e}")

    def run(self) -> dict:
        """Execute wireless scan"""
        try:
            self.logger.attack("Starting wireless network scan")

            # Start channel hopping
            if self.channel_hop:
                import threading
                self.hop_thread = threading.Thread(target=self._channel_hopper)
                self.hop_thread.daemon = True
                self.hop_thread.start()

            # Start packet capture
            self.packet_handler.add_callback(self._process_packet)
            self.packet_handler.start_capture()

            # Scan for duration
            start_time = time.time()
            while not self._stop_event.is_set():
                if time.time() - start_time > self.scan_duration:
                    break
                time.sleep(1)

            # Stop capture
            self.packet_handler.stop_capture()

            # Get results
            aps = self.device_manager.get_all_aps()
            clients = self.device_manager.get_all_clients()

            self.logger.success(f"Scan complete: Found {len(aps)} APs and {len(clients)} clients")

            return {
                'success': True,
                'access_points': [ap.to_dict() for ap in aps],
                'clients': [client.to_dict() for client in clients],
                'total_aps': len(aps),
                'total_clients': len(clients)
            }

        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the scan"""
        self._stop_event.set()
        if self.packet_handler:
            self.packet_handler.stop_capture()

    def cleanup(self):
        """Cleanup resources"""
        if self.packet_handler:
            self.packet_handler.stop_capture()

    def get_access_points(self) -> List[WirelessDevice]:
        """Get discovered access points"""
        return self.device_manager.get_all_aps()

    def get_clients(self) -> List[WirelessDevice]:
        """Get discovered clients"""
        return self.device_manager.get_all_clients()

    def get_ap_by_ssid(self, ssid: str) -> WirelessDevice:
        """Get AP by SSID"""
        return self.device_manager.get_ap_by_ssid(ssid)


class NetworkScanner(BaseModule):
    """
    Network layer scanner
    Discovers hosts on the local network
    """

    def __init__(self):
        super().__init__(
            name="Network Scanner",
            description="Scan for devices on the local network"
        )
        self.network = None
        self.timeout = 2
        self.discovered_hosts = []

    def setup(self, **kwargs) -> bool:
        """
        Setup network scanner
        Args:
            interface: Network interface
            network: Network to scan (e.g., '192.168.1.0/24')
            timeout: Scan timeout
        """
        try:
            self.interface = kwargs.get('interface')
            self.network = kwargs.get('network')
            self.timeout = kwargs.get('timeout', 2)

            if not self.interface or not self.network:
                self.logger.error("Interface and network required")
                return False

            self.logger.info(f"Network scanner configured:")
            self.logger.info(f"  Network: {self.network}")
            self.logger.info(f"  Timeout: {self.timeout}s")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def run(self) -> dict:
        """Execute network scan"""
        try:
            self.logger.attack(f"Scanning network {self.network}")

            # ARP scan
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=self.network),
                timeout=self.timeout,
                verbose=False,
                iface=self.interface
            )

            # Process responses
            for sent, received in ans:
                ip = received[ARP].psrc
                mac = received[Ether].src
                vendor = get_mac_vendor(mac)

                host = NetworkDevice(
                    ip=ip,
                    mac=mac,
                    vendor=vendor
                )
                self.discovered_hosts.append(host)

                self.logger.info(f"Host found: {ip} ({mac}) - {vendor}")

            self.logger.success(f"Scan complete: Found {len(self.discovered_hosts)} hosts")

            return {
                'success': True,
                'hosts': [host.to_dict() for host in self.discovered_hosts],
                'total_hosts': len(self.discovered_hosts)
            }

        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the scan"""
        self._stop_event.set()

    def cleanup(self):
        """Cleanup resources"""
        pass

    def get_hosts(self) -> List[NetworkDevice]:
        """Get discovered hosts"""
        return self.discovered_hosts
