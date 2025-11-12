"""
Wireless Intrusion Detection System (IDS)
Detects and alerts on wireless attacks
"""

from scapy.all import *
from darknet.core.base import DefenseModule
from darknet.core.packet import PacketHandler
from darknet.utils.constants import *
from darknet.utils.logger import setup_logger
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class WirelessIDS(DefenseModule):
    """
    Comprehensive Wireless IDS
    Detects deauth attacks, rogue APs, evil twins, beacon floods, and more
    """

    def __init__(self):
        super().__init__(
            name="Wireless IDS",
            description="Comprehensive wireless intrusion detection system",
            detection_type="all"
        )
        self.packet_handler = None

        # Detection thresholds
        self.deauth_threshold = 10  # Deauth packets per minute
        self.beacon_threshold = 100  # Beacons per minute for flood detection
        self.probe_threshold = 50  # Probe requests per minute

        # Tracking dictionaries
        self.deauth_count = defaultdict(list)  # BSSID -> [timestamps]
        self.beacon_count = defaultdict(list)  # BSSID -> [timestamps]
        self.probe_count = defaultdict(list)  # Client MAC -> [timestamps]
        self.known_aps = {}  # BSSID -> {ssid, channel, encryption}
        self.suspicious_aps = set()

        # Alert cooldown
        self.alert_cooldown = {}  # threat_id -> last_alert_time
        self.cooldown_period = 60  # seconds

    def setup(self, **kwargs) -> bool:
        """
        Setup wireless IDS
        Args:
            interface: Wireless interface in monitor mode
            deauth_threshold: Deauth packets per minute to trigger alert
            beacon_threshold: Beacons per minute to trigger alert
            probe_threshold: Probe requests per minute to trigger alert
        """
        try:
            self.interface = kwargs.get('interface')
            self.deauth_threshold = kwargs.get('deauth_threshold', 10)
            self.beacon_threshold = kwargs.get('beacon_threshold', 100)
            self.probe_threshold = kwargs.get('probe_threshold', 50)

            if not self.interface:
                self.logger.error("Interface required")
                return False

            self.packet_handler = PacketHandler(self.interface)

            self.logger.info(f"Wireless IDS configured:")
            self.logger.info(f"  Interface: {self.interface}")
            self.logger.info(f"  Deauth threshold: {self.deauth_threshold}/min")
            self.logger.info(f"  Beacon threshold: {self.beacon_threshold}/min")
            self.logger.info(f"  Probe threshold: {self.probe_threshold}/min")

            return True

        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

    def _should_alert(self, threat_id: str) -> bool:
        """Check if we should alert (cooldown check)"""
        now = datetime.now()
        if threat_id in self.alert_cooldown:
            last_alert = self.alert_cooldown[threat_id]
            if (now - last_alert).seconds < self.cooldown_period:
                return False

        self.alert_cooldown[threat_id] = now
        return True

    def _raise_alert(self, threat_type: str, severity: str, details: dict):
        """Raise a security alert"""
        threat = {
            'type': threat_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }

        self.add_threat(threat)

        # Log based on severity
        if severity == SEVERITY_CRITICAL:
            self.logger.critical(f"CRITICAL THREAT: {threat_type}")
        elif severity == SEVERITY_HIGH:
            self.logger.error(f"HIGH THREAT: {threat_type}")
        elif severity == SEVERITY_MEDIUM:
            self.logger.warning(f"MEDIUM THREAT: {threat_type}")
        else:
            self.logger.info(f"LOW THREAT: {threat_type}")

        self.logger.defense(f"Details: {details}")

    def _clean_old_timestamps(self, timestamp_list: list, window_minutes: int = 1):
        """Remove timestamps older than window"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        return [ts for ts in timestamp_list if ts > cutoff]

    def _detect_deauth_attack(self, packet):
        """Detect deauthentication attacks"""
        try:
            if packet.haslayer(Dot11Deauth) or packet.haslayer(Dot11Disas):
                bssid = packet[Dot11].addr3
                now = datetime.now()

                # Track deauth packets
                self.deauth_count[bssid].append(now)
                self.deauth_count[bssid] = self._clean_old_timestamps(self.deauth_count[bssid])

                count = len(self.deauth_count[bssid])

                # Check threshold
                if count >= self.deauth_threshold:
                    threat_id = f"deauth_{bssid}"
                    if self._should_alert(threat_id):
                        self._raise_alert(
                            DETECT_DEAUTH_ATTACK,
                            SEVERITY_HIGH,
                            {
                                'bssid': bssid,
                                'count': count,
                                'reason': packet[Dot11Deauth].reason if packet.haslayer(Dot11Deauth) else 'disassoc',
                                'client': packet[Dot11].addr1
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Error detecting deauth: {e}")

    def _detect_beacon_flood(self, packet):
        """Detect beacon flooding attacks"""
        try:
            if packet.haslayer(Dot11Beacon):
                bssid = packet[Dot11].addr3
                now = datetime.now()

                # Track beacon packets
                self.beacon_count[bssid].append(now)
                self.beacon_count[bssid] = self._clean_old_timestamps(self.beacon_count[bssid])

                count = len(self.beacon_count[bssid])

                # Check threshold
                if count >= self.beacon_threshold:
                    threat_id = f"beacon_flood_{bssid}"
                    if self._should_alert(threat_id):
                        ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore') if packet[Dot11Elt].info else ""
                        self._raise_alert(
                            DETECT_BEACON_FLOOD,
                            SEVERITY_MEDIUM,
                            {
                                'bssid': bssid,
                                'ssid': ssid,
                                'beacon_rate': count
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Error detecting beacon flood: {e}")

    def _detect_evil_twin(self, packet):
        """Detect evil twin / rogue AP attacks"""
        try:
            if packet.haslayer(Dot11Beacon):
                bssid = packet[Dot11].addr3
                ssid = packet[Dot11Elt].info.decode('utf-8', errors='ignore') if packet[Dot11Elt].info else ""
                channel = PacketHandler.get_channel_from_packet(packet)
                encryption = PacketHandler.get_encryption_type(packet)

                # Check if we've seen this AP before
                if bssid in self.known_aps:
                    known = self.known_aps[bssid]

                    # Check for mismatches (evil twin indicators)
                    if known['ssid'] != ssid or known['channel'] != channel:
                        threat_id = f"evil_twin_{bssid}"
                        if self._should_alert(threat_id):
                            self._raise_alert(
                                DETECT_EVIL_TWIN,
                                SEVERITY_CRITICAL,
                                {
                                    'bssid': bssid,
                                    'known_ssid': known['ssid'],
                                    'current_ssid': ssid,
                                    'known_channel': known['channel'],
                                    'current_channel': channel
                                }
                            )
                else:
                    # Learn new AP
                    self.known_aps[bssid] = {
                        'ssid': ssid,
                        'channel': channel,
                        'encryption': encryption
                    }

                # Check for duplicate SSID on different BSSID
                for known_bssid, info in self.known_aps.items():
                    if known_bssid != bssid and info['ssid'] == ssid and ssid:
                        threat_id = f"duplicate_ssid_{ssid}"
                        if self._should_alert(threat_id):
                            self._raise_alert(
                                DETECT_EVIL_TWIN,
                                SEVERITY_HIGH,
                                {
                                    'ssid': ssid,
                                    'bssid_1': known_bssid,
                                    'bssid_2': bssid,
                                    'message': 'Multiple APs with same SSID detected'
                                }
                            )

        except Exception as e:
            self.logger.debug(f"Error detecting evil twin: {e}")

    def _detect_probe_flood(self, packet):
        """Detect probe request flooding"""
        try:
            if packet.haslayer(Dot11ProbeReq):
                client_mac = packet[Dot11].addr2
                now = datetime.now()

                # Track probe requests
                self.probe_count[client_mac].append(now)
                self.probe_count[client_mac] = self._clean_old_timestamps(self.probe_count[client_mac])

                count = len(self.probe_count[client_mac])

                # Check threshold
                if count >= self.probe_threshold:
                    threat_id = f"probe_flood_{client_mac}"
                    if self._should_alert(threat_id):
                        self._raise_alert(
                            DETECT_PROBE_REQUEST_FLOOD,
                            SEVERITY_MEDIUM,
                            {
                                'client_mac': client_mac,
                                'probe_rate': count
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Error detecting probe flood: {e}")

    def _detect_handshake_capture(self, packet):
        """Detect potential handshake capture attempts"""
        try:
            if packet.haslayer(EAPOL):
                bssid = packet[Dot11].addr3 if packet.haslayer(Dot11) else None

                if bssid:
                    threat_id = f"handshake_{bssid}"
                    if self._should_alert(threat_id):
                        self._raise_alert(
                            DETECT_HANDSHAKE_CAPTURE,
                            SEVERITY_MEDIUM,
                            {
                                'bssid': bssid,
                                'message': 'EAPOL handshake detected - possible capture attempt'
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Error detecting handshake capture: {e}")

    def analyze_packet(self, packet) -> Optional[Dict[str, Any]]:
        """Analyze packet for threats"""
        # Run all detections
        self._detect_deauth_attack(packet)
        self._detect_beacon_flood(packet)
        self._detect_evil_twin(packet)
        self._detect_probe_flood(packet)
        self._detect_handshake_capture(packet)

        return None

    def _packet_callback(self, packet):
        """Packet callback for analysis"""
        try:
            if packet.haslayer(Dot11):
                self.analyze_packet(packet)
        except Exception as e:
            self.logger.debug(f"Error in packet callback: {e}")

    def run(self) -> dict:
        """Execute wireless IDS"""
        try:
            self.logger.defense("Starting Wireless IDS")
            self.logger.info("Monitoring for wireless attacks...")

            # Start packet capture
            self.packet_handler.add_callback(self._packet_callback)
            self.packet_handler.start_capture()

            # Monitor until stopped
            while not self._stop_event.is_set():
                time.sleep(1)

            self.packet_handler.stop_capture()

            self.logger.info("Wireless IDS stopped")
            self.logger.info(f"Total threats detected: {len(self.threats_detected)}")

            return {
                'success': True,
                'threats_detected': self.threats_detected,
                'total_threats': len(self.threats_detected),
                'statistics': self.get_statistics()
            }

        except Exception as e:
            self.logger.error(f"IDS failed: {e}")
            return {'success': False, 'error': str(e)}

    def stop(self):
        """Stop the IDS"""
        self._stop_event.set()
        if self.packet_handler:
            self.packet_handler.stop_capture()

    def cleanup(self):
        """Cleanup resources"""
        if self.packet_handler:
            self.packet_handler.stop_capture()
