"""
Packet handling and manipulation for Darknet framework
"""

from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, Dot11Auth, Dot11Deauth, Dot11Disas, RadioTap
from scapy.layers.eap import EAPOL
from typing import Optional, List, Dict, Any, Callable
import threading
from collections import defaultdict
from darknet.utils.constants import *
from darknet.utils.logger import setup_logger


class PacketHandler:
    """Handler for wireless packet operations"""

    def __init__(self, interface: str):
        self.interface = interface
        self.logger = setup_logger("PacketHandler")
        self.capture_running = False
        self.capture_thread = None
        self.packet_callbacks = []
        self.captured_packets = []
        self.packet_count = defaultdict(int)

    def add_callback(self, callback: Callable):
        """Add a callback function to be called for each captured packet"""
        self.packet_callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.packet_callbacks:
            self.packet_callbacks.remove(callback)

    def _packet_handler(self, packet):
        """Internal packet handler"""
        try:
            self.captured_packets.append(packet)

            # Update packet count by type
            if packet.haslayer(Dot11):
                pkt_type = packet.type
                self.packet_count[pkt_type] += 1

            # Call all registered callbacks
            for callback in self.packet_callbacks:
                try:
                    callback(packet)
                except Exception as e:
                    self.logger.error(f"Error in packet callback: {e}")

        except Exception as e:
            self.logger.error(f"Error handling packet: {e}")

    def start_capture(self, packet_filter: Optional[str] = None, count: int = 0):
        """
        Start capturing packets
        Args:
            packet_filter: BPF filter string
            count: Number of packets to capture (0 = infinite)
        """
        if self.capture_running:
            self.logger.warning("Capture already running")
            return

        self.capture_running = True
        self.captured_packets.clear()
        self.packet_count.clear()

        def capture():
            try:
                sniff(
                    iface=self.interface,
                    prn=self._packet_handler,
                    filter=packet_filter,
                    count=count,
                    store=False,
                    stop_filter=lambda x: not self.capture_running
                )
            except Exception as e:
                self.logger.error(f"Capture error: {e}")
            finally:
                self.capture_running = False

        self.capture_thread = threading.Thread(target=capture)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        self.logger.info(f"Started packet capture on {self.interface}")

    def stop_capture(self):
        """Stop packet capture"""
        self.capture_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        self.logger.info("Stopped packet capture")

    def send_packet(self, packet, count: int = 1, inter: float = 0, verbose: bool = False):
        """
        Send packet(s)
        Args:
            packet: Scapy packet to send
            count: Number of times to send
            inter: Interval between packets
            verbose: Print packet info
        """
        try:
            sendp(packet, iface=self.interface, count=count, inter=inter, verbose=verbose)
            return True
        except Exception as e:
            self.logger.error(f"Error sending packet: {e}")
            return False

    def inject_packets(self, packets: List, rate: int = 50):
        """
        Inject multiple packets at specified rate
        Args:
            packets: List of packets to inject
            rate: Packets per second
        """
        inter = 1.0 / rate if rate > 0 else 0
        try:
            for packet in packets:
                self.send_packet(packet, count=1, inter=inter)
            return True
        except Exception as e:
            self.logger.error(f"Error injecting packets: {e}")
            return False

    def get_packet_count(self) -> Dict[int, int]:
        """Get count of packets by type"""
        return dict(self.packet_count)

    def get_captured_packets(self) -> List:
        """Get all captured packets"""
        return self.captured_packets

    def clear_captured_packets(self):
        """Clear captured packets from memory"""
        self.captured_packets.clear()
        self.packet_count.clear()

    def save_pcap(self, filename: str):
        """Save captured packets to pcap file"""
        try:
            wrpcap(filename, self.captured_packets)
            self.logger.success(f"Saved {len(self.captured_packets)} packets to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving pcap: {e}")
            return False

    @staticmethod
    def create_deauth_packet(target_mac: str, ap_mac: str, reason: int = 7) -> Packet:
        """
        Create a deauthentication packet
        Args:
            target_mac: Target client MAC address
            ap_mac: Access Point MAC address
            reason: Deauth reason code
        """
        packet = RadioTap() / Dot11(
            type=0,
            subtype=12,
            addr1=target_mac,
            addr2=ap_mac,
            addr3=ap_mac
        ) / Dot11Deauth(reason=reason)
        return packet

    @staticmethod
    def create_disassoc_packet(target_mac: str, ap_mac: str, reason: int = 7) -> Packet:
        """
        Create a disassociation packet
        Args:
            target_mac: Target client MAC address
            ap_mac: Access Point MAC address
            reason: Disassoc reason code
        """
        packet = RadioTap() / Dot11(
            type=0,
            subtype=10,
            addr1=target_mac,
            addr2=ap_mac,
            addr3=ap_mac
        ) / Dot11Disas(reason=reason)
        return packet

    @staticmethod
    def create_beacon_packet(ssid: str, mac: str, channel: int, encryption: str = "WPA2") -> Packet:
        """
        Create a beacon frame packet
        Args:
            ssid: Network SSID
            mac: BSSID (MAC address)
            channel: WiFi channel
            encryption: Encryption type
        """
        dot11 = Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=mac, addr3=mac)
        beacon = Dot11Beacon(cap='ESS+privacy')
        essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))

        # DS Parameter set
        dsset = Dot11Elt(ID='DSset', info=chr(channel))

        # Build the packet
        packet = RadioTap() / dot11 / beacon / essid / dsset

        if encryption != "OPEN":
            # Add RSN information for WPA2/WPA3
            rsn = Dot11Elt(ID='RSNinfo', info=(
                '\x01\x00'  # RSN Version 1
                '\x00\x0f\xac\x04'  # Group Cipher Suite: AES (CCM)
                '\x01\x00'  # Pairwise Cipher Suite Count
                '\x00\x0f\xac\x04'  # Pairwise Cipher Suite: AES (CCM)
                '\x01\x00'  # AKM Suite Count
                '\x00\x0f\xac\x02'  # PSK
                '\x00\x00'  # RSN Capabilities
            ))
            packet = packet / rsn

        return packet

    @staticmethod
    def create_probe_request(ssid: str = "", src_mac: str = "00:11:22:33:44:55") -> Packet:
        """
        Create a probe request packet
        Args:
            ssid: Target SSID (empty for broadcast)
            src_mac: Source MAC address
        """
        dot11 = Dot11(type=0, subtype=4, addr1="ff:ff:ff:ff:ff:ff", addr2=src_mac, addr3="ff:ff:ff:ff:ff:ff")
        essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))
        packet = RadioTap() / dot11 / Dot11ProbeReq() / essid
        return packet

    @staticmethod
    def is_handshake_packet(packet) -> bool:
        """Check if packet is part of WPA handshake"""
        if packet.haslayer(EAPOL):
            return True
        return False

    @staticmethod
    def extract_ssid(packet) -> Optional[str]:
        """Extract SSID from packet"""
        try:
            if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
                ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore')
                return ssid if ssid else None
        except Exception:
            pass
        return None

    @staticmethod
    def extract_bssid(packet) -> Optional[str]:
        """Extract BSSID (AP MAC) from packet"""
        try:
            if packet.haslayer(Dot11):
                return packet[Dot11].addr3
        except Exception:
            pass
        return None

    @staticmethod
    def extract_client_mac(packet) -> Optional[str]:
        """Extract client MAC address from packet"""
        try:
            if packet.haslayer(Dot11):
                # Check if packet is from client to AP
                if packet.FCfield & 0x1:  # To DS flag
                    return packet[Dot11].addr2
                # Check if packet is from AP to client
                elif packet.FCfield & 0x2:  # From DS flag
                    return packet[Dot11].addr1
        except Exception:
            pass
        return None

    @staticmethod
    def get_encryption_type(packet) -> str:
        """Determine encryption type from packet"""
        try:
            if packet.haslayer(Dot11Beacon):
                cap = packet[Dot11Beacon].cap

                # Check for privacy bit
                if not (cap & 0x10):
                    return ENCRYPTION_OPEN

                # Check for RSN (WPA2/WPA3)
                if packet.haslayer(Dot11Elt):
                    elt = packet[Dot11Elt]
                    while isinstance(elt, Dot11Elt):
                        if elt.ID == 48:  # RSN Information
                            # Could be WPA2 or WPA3
                            return ENCRYPTION_WPA2
                        elif elt.ID == 221:  # Vendor Specific (WPA)
                            return ENCRYPTION_WPA
                        elt = elt.payload

                # If privacy but no RSN/WPA, probably WEP
                return ENCRYPTION_WEP
        except Exception:
            pass
        return "UNKNOWN"

    @staticmethod
    def get_channel_from_packet(packet) -> Optional[int]:
        """Extract channel from packet"""
        try:
            if packet.haslayer(Dot11Elt):
                elt = packet[Dot11Elt]
                while isinstance(elt, Dot11Elt):
                    if elt.ID == 3:  # DS Parameter set
                        return ord(elt.info)
                    elt = elt.payload
        except Exception:
            pass
        return None

    @staticmethod
    def get_signal_strength(packet) -> Optional[int]:
        """Get signal strength from packet (dBm)"""
        try:
            if packet.haslayer(RadioTap):
                return packet[RadioTap].dBm_AntSignal
        except Exception:
            pass
        return None
