"""
Device management for Darknet framework
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from datetime import datetime
from darknet.utils.constants import *


@dataclass
class WirelessDevice:
    """Represents a wireless device (AP or client)"""
    mac: str
    ssid: Optional[str] = None
    channel: Optional[int] = None
    encryption: str = ENCRYPTION_OPEN
    signal_strength: int = -100
    vendor: str = "Unknown"
    device_type: str = "unknown"  # 'ap' or 'client'
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    packets: int = 0
    data_bytes: int = 0
    connected_clients: Set[str] = field(default_factory=set)
    beacons: int = 0
    data_packets: int = 0
    handshake_captured: bool = False
    pmkid_captured: bool = False
    associated_ap: Optional[str] = None  # For clients
    probe_requests: List[str] = field(default_factory=list)

    def update(self, **kwargs):
        """Update device properties"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_seen = datetime.now()

    def add_client(self, client_mac: str):
        """Add a connected client"""
        self.connected_clients.add(client_mac)

    def remove_client(self, client_mac: str):
        """Remove a connected client"""
        self.connected_clients.discard(client_mac)

    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)

    def is_hidden(self) -> bool:
        """Check if SSID is hidden"""
        return self.ssid is None or self.ssid == ""

    def is_wpa_enterprise(self) -> bool:
        """Check if using WPA Enterprise"""
        return self.encryption in [ENCRYPTION_WPA, ENCRYPTION_WPA2, ENCRYPTION_WPA3]

    def get_age(self) -> float:
        """Get age of device in seconds"""
        return (datetime.now() - self.first_seen).total_seconds()

    def get_last_seen_seconds(self) -> float:
        """Get seconds since last seen"""
        return (datetime.now() - self.last_seen).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'mac': self.mac,
            'ssid': self.ssid,
            'channel': self.channel,
            'encryption': self.encryption,
            'signal_strength': self.signal_strength,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'packets': self.packets,
            'data_bytes': self.data_bytes,
            'connected_clients': list(self.connected_clients),
            'beacons': self.beacons,
            'data_packets': self.data_packets,
            'handshake_captured': self.handshake_captured,
            'pmkid_captured': self.pmkid_captured,
            'associated_ap': self.associated_ap,
            'probe_requests': self.probe_requests
        }


@dataclass
class NetworkDevice:
    """Represents a network layer device (for MITM attacks)"""
    ip: str
    mac: str
    hostname: Optional[str] = None
    vendor: str = "Unknown"
    device_type: str = "unknown"
    open_ports: List[int] = field(default_factory=list)
    os_guess: Optional[str] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    connections: List[str] = field(default_factory=list)
    is_gateway: bool = False
    is_target: bool = False

    def update(self, **kwargs):
        """Update device properties"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_seen = datetime.now()

    def add_port(self, port: int):
        """Add an open port"""
        if port not in self.open_ports:
            self.open_ports.append(port)
            self.open_ports.sort()

    def add_connection(self, connection: str):
        """Add a connection"""
        if connection not in self.connections:
            self.connections.append(connection)

    def increment_traffic(self, sent: int = 0, received: int = 0):
        """Increment traffic counters"""
        self.packets_sent += 1 if sent > 0 else 0
        self.packets_received += 1 if received > 0 else 0
        self.bytes_sent += sent
        self.bytes_received += received
        self.last_seen = datetime.now()

    def get_total_bytes(self) -> int:
        """Get total bytes transferred"""
        return self.bytes_sent + self.bytes_received

    def get_last_seen_seconds(self) -> float:
        """Get seconds since last seen"""
        return (datetime.now() - self.last_seen).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'ip': self.ip,
            'mac': self.mac,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'open_ports': self.open_ports,
            'os_guess': self.os_guess,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'connections': self.connections,
            'is_gateway': self.is_gateway,
            'is_target': self.is_target
        }


class DeviceManager:
    """Manager for tracking wireless and network devices"""

    def __init__(self):
        self.wireless_devices = {}  # MAC -> WirelessDevice
        self.network_devices = {}  # IP -> NetworkDevice
        self.access_points = {}  # MAC -> WirelessDevice (APs only)
        self.clients = {}  # MAC -> WirelessDevice (clients only)

    def add_wireless_device(self, device: WirelessDevice):
        """Add or update wireless device"""
        self.wireless_devices[device.mac] = device

        if device.device_type == 'ap':
            self.access_points[device.mac] = device
        elif device.device_type == 'client':
            self.clients[device.mac] = device

    def add_network_device(self, device: NetworkDevice):
        """Add or update network device"""
        self.network_devices[device.ip] = device

    def get_wireless_device(self, mac: str) -> Optional[WirelessDevice]:
        """Get wireless device by MAC"""
        return self.wireless_devices.get(mac)

    def get_network_device(self, ip: str) -> Optional[NetworkDevice]:
        """Get network device by IP"""
        return self.network_devices.get(ip)

    def get_ap_by_ssid(self, ssid: str) -> Optional[WirelessDevice]:
        """Get access point by SSID"""
        for ap in self.access_points.values():
            if ap.ssid == ssid:
                return ap
        return None

    def get_all_aps(self) -> List[WirelessDevice]:
        """Get all access points"""
        return list(self.access_points.values())

    def get_all_clients(self) -> List[WirelessDevice]:
        """Get all clients"""
        return list(self.clients.values())

    def get_all_network_devices(self) -> List[NetworkDevice]:
        """Get all network devices"""
        return list(self.network_devices.values())

    def get_aps_by_encryption(self, encryption: str) -> List[WirelessDevice]:
        """Get APs by encryption type"""
        return [ap for ap in self.access_points.values() if ap.encryption == encryption]

    def get_clients_for_ap(self, ap_mac: str) -> List[WirelessDevice]:
        """Get all clients connected to an AP"""
        return [client for client in self.clients.values() if client.associated_ap == ap_mac]

    def remove_wireless_device(self, mac: str):
        """Remove wireless device"""
        self.wireless_devices.pop(mac, None)
        self.access_points.pop(mac, None)
        self.clients.pop(mac, None)

    def remove_network_device(self, ip: str):
        """Remove network device"""
        self.network_devices.pop(ip, None)

    def clear_all(self):
        """Clear all devices"""
        self.wireless_devices.clear()
        self.network_devices.clear()
        self.access_points.clear()
        self.clients.clear()

    def get_device_count(self) -> dict:
        """Get count of each device type"""
        return {
            'total_wireless': len(self.wireless_devices),
            'access_points': len(self.access_points),
            'clients': len(self.clients),
            'network_devices': len(self.network_devices)
        }
