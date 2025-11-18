"""
Pattern detection and alert system for identifying suspicious device behavior.
Detects tracking patterns, surveillance, and following devices.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class PatternDetector:
    """Detect suspicious patterns in device sightings."""

    def __init__(self, db):
        """
        Initialize pattern detector.

        Args:
            db: DeviceDatabase instance
        """
        self.db = db
        self.threat_thresholds = {
            'LOW': 2,      # Seen 2-3 times
            'MEDIUM': 4,   # Seen 4-6 times
            'HIGH': 7,     # Seen 7-10 times
            'CRITICAL': 11 # Seen 11+ times
        }

    def analyze_device(self, device_id: int) -> Dict:
        """
        Analyze a specific device for suspicious patterns.

        Returns:
            Analysis results with threat assessment
        """
        device = self.db.get_device_by_mac(
            self.db.get_all_devices()[0]['mac_address']
        )
        sightings = self.db.get_device_sightings(device_id)

        analysis = {
            'device_id': device_id,
            'threat_level': 'LOW',
            'threat_score': 0,
            'suspicious_patterns': [],
            'recommendations': []
        }

        if not sightings:
            return analysis

        # Pattern 1: Multiple sightings (basic tracking indicator)
        sightings_count = len(sightings)
        if sightings_count >= 3:
            analysis['suspicious_patterns'].append({
                'type': 'MULTIPLE_SIGHTINGS',
                'description': f'Device seen {sightings_count} times',
                'severity': self._get_severity_from_count(sightings_count)
            })
            analysis['threat_score'] += sightings_count * 2

        # Pattern 2: Temporal analysis (appearing at consistent times)
        temporal_pattern = self._analyze_temporal_pattern(sightings)
        if temporal_pattern:
            analysis['suspicious_patterns'].append(temporal_pattern)
            analysis['threat_score'] += 15

        # Pattern 3: Location correlation (multiple different contexts)
        location_pattern = self._analyze_location_pattern(sightings)
        if location_pattern:
            analysis['suspicious_patterns'].append(location_pattern)
            analysis['threat_score'] += 20

        # Pattern 4: Signal strength analysis (device getting closer/following)
        signal_pattern = self._analyze_signal_strength(sightings)
        if signal_pattern:
            analysis['suspicious_patterns'].append(signal_pattern)
            analysis['threat_score'] += 10

        # Pattern 5: Recent activity burst (suddenly appearing frequently)
        burst_pattern = self._analyze_activity_burst(sightings)
        if burst_pattern:
            analysis['suspicious_patterns'].append(burst_pattern)
            analysis['threat_score'] += 25

        # Determine overall threat level
        analysis['threat_level'] = self._calculate_threat_level(
            analysis['threat_score']
        )

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _get_severity_from_count(self, count: int) -> str:
        """Determine severity based on sighting count."""
        if count >= 11:
            return 'CRITICAL'
        elif count >= 7:
            return 'HIGH'
        elif count >= 4:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _analyze_temporal_pattern(self, sightings: List[Dict]) -> Optional[Dict]:
        """
        Analyze if device appears at consistent times.
        Could indicate scheduled surveillance.
        """
        if len(sightings) < 3:
            return None

        timestamps = []
        for sighting in sightings:
            try:
                dt = datetime.fromisoformat(sighting['timestamp'])
                timestamps.append(dt)
            except:
                continue

        if len(timestamps) < 3:
            return None

        # Check for time-of-day patterns
        hours = [dt.hour for dt in timestamps]
        if len(set(hours)) < len(hours) * 0.5:  # 50% or more at same hours
            return {
                'type': 'TEMPORAL_PATTERN',
                'description': f'Device appears at consistent times (hours: {sorted(set(hours))})',
                'severity': 'MEDIUM'
            }

        # Check for day-of-week patterns
        weekdays = [dt.weekday() for dt in timestamps]
        if len(set(weekdays)) < len(weekdays) * 0.6:  # 60% or more on same days
            return {
                'type': 'TEMPORAL_PATTERN',
                'description': 'Device appears on consistent days of the week',
                'severity': 'MEDIUM'
            }

        return None

    def _analyze_location_pattern(self, sightings: List[Dict]) -> Optional[Dict]:
        """
        Analyze location contexts to detect following.
        If device appears at multiple different locations, it's tracking you.
        """
        if len(sightings) < 3:
            return None

        locations = [s.get('location_context') for s in sightings if s.get('location_context')]

        if len(set(locations)) >= 3:
            return {
                'type': 'MULTI_LOCATION',
                'description': f'Device seen at {len(set(locations))} different locations: {", ".join(set(locations))}',
                'severity': 'HIGH'
            }

        return None

    def _analyze_signal_strength(self, sightings: List[Dict]) -> Optional[Dict]:
        """
        Analyze signal strength changes.
        Increasing strength could mean device is getting closer.
        """
        if len(sightings) < 4:
            return None

        signals = []
        for sighting in sightings:
            if sighting.get('signal_strength') is not None:
                signals.append((
                    datetime.fromisoformat(sighting['timestamp']),
                    sighting['signal_strength']
                ))

        if len(signals) < 4:
            return None

        # Sort by time
        signals.sort(key=lambda x: x[0])

        # Check if signal is consistently increasing (getting closer)
        recent_signals = [s[1] for s in signals[-5:]]  # Last 5 signals
        if len(recent_signals) >= 4:
            # Check for upward trend
            increasing_count = sum(
                1 for i in range(len(recent_signals) - 1)
                if recent_signals[i + 1] > recent_signals[i]
            )

            if increasing_count >= len(recent_signals) - 2:
                return {
                    'type': 'APPROACHING',
                    'description': 'Device signal strength increasing - may be getting closer',
                    'severity': 'HIGH'
                }

        return None

    def _analyze_activity_burst(self, sightings: List[Dict]) -> Optional[Dict]:
        """
        Detect sudden bursts of activity.
        Many sightings in short time = active surveillance.
        """
        if len(sightings) < 3:
            return None

        timestamps = []
        for sighting in sightings:
            try:
                dt = datetime.fromisoformat(sighting['timestamp'])
                timestamps.append(dt)
            except:
                continue

        if len(timestamps) < 3:
            return None

        # Sort by time
        timestamps.sort()

        # Check last 24 hours
        now = datetime.now()
        recent = [ts for ts in timestamps if (now - ts).total_seconds() < 86400]

        if len(recent) >= 5:
            return {
                'type': 'ACTIVITY_BURST',
                'description': f'{len(recent)} sightings in the last 24 hours - active surveillance suspected',
                'severity': 'CRITICAL'
            }

        # Check last hour
        very_recent = [ts for ts in timestamps if (now - ts).total_seconds() < 3600]
        if len(very_recent) >= 3:
            return {
                'type': 'ACTIVITY_BURST',
                'description': f'{len(very_recent)} sightings in the last hour - active tracking',
                'severity': 'CRITICAL'
            }

        return None

    def _calculate_threat_level(self, threat_score: int) -> str:
        """Calculate overall threat level from score."""
        if threat_score >= 50:
            return 'CRITICAL'
        elif threat_score >= 30:
            return 'HIGH'
        elif threat_score >= 15:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        threat_level = analysis['threat_level']

        if threat_level in ['HIGH', 'CRITICAL']:
            recommendations.append('⚠️  HIGH RISK: Consider taking immediate action')
            recommendations.append('Change your location and monitor if device follows')
            recommendations.append('Document all sightings with timestamps and locations')
            recommendations.append('Consider contacting law enforcement if pattern persists')

        if threat_level in ['MEDIUM', 'HIGH', 'CRITICAL']:
            recommendations.append('Add notes to this device for future reference')
            recommendations.append('Enable location context tracking for better analysis')
            recommendations.append('Run continuous monitoring to gather more data')

        if any(p['type'] == 'APPROACHING' for p in analysis['suspicious_patterns']):
            recommendations.append('⚠️  Device signal strengthening - may be approaching you')
            recommendations.append('Leave area and monitor if device follows')

        if any(p['type'] == 'MULTI_LOCATION' for p in analysis['suspicious_patterns']):
            recommendations.append('🚨 TRACKING CONFIRMED: Device seen at multiple locations')
            recommendations.append('This is strong evidence of active tracking')

        if any(p['type'] == 'ACTIVITY_BURST' for p in analysis['suspicious_patterns']):
            recommendations.append('🚨 ACTIVE SURVEILLANCE: Multiple recent sightings detected')
            recommendations.append('Take evasive action immediately')

        if not recommendations:
            recommendations.append('Continue monitoring this device')
            recommendations.append('Note location context when device is sighted')

        return recommendations

    def scan_all_devices_for_threats(self) -> List[Dict]:
        """
        Scan all devices in database for threats.

        Returns:
            List of threat analyses for suspicious devices
        """
        all_devices = self.db.get_all_devices()
        threats = []

        for device in all_devices:
            analysis = self.analyze_device(device['id'])

            # Only include devices with threats
            if analysis['threat_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']:
                analysis['device'] = device
                threats.append(analysis)

        # Sort by threat score
        threats.sort(key=lambda x: x['threat_score'], reverse=True)

        return threats

    def check_and_create_alerts(self, device_id: int) -> List[str]:
        """
        Check device and create alerts if threats detected.

        Returns:
            List of alert messages
        """
        analysis = self.analyze_device(device_id)
        alerts = []

        # Create alerts for significant threats
        if analysis['threat_level'] in ['HIGH', 'CRITICAL']:
            message = f"Threat level {analysis['threat_level']} detected. "
            message += f"Threat score: {analysis['threat_score']}. "
            message += f"Patterns: {', '.join([p['type'] for p in analysis['suspicious_patterns']])}"

            self.db.create_alert(
                device_id,
                f"THREAT_{analysis['threat_level']}",
                message
            )
            alerts.append(message)

            # Update device threat level in database
            self.db.update_threat_level(device_id, analysis['threat_level'])

        return alerts

    def get_threat_summary(self) -> Dict:
        """Get summary of all threats in database."""
        stats = self.db.get_statistics()
        threats = self.scan_all_devices_for_threats()

        summary = {
            'total_devices': stats['total_devices'],
            'suspicious_devices': len(threats),
            'critical_threats': len([t for t in threats if t['threat_level'] == 'CRITICAL']),
            'high_threats': len([t for t in threats if t['threat_level'] == 'HIGH']),
            'medium_threats': len([t for t in threats if t['threat_level'] == 'MEDIUM']),
            'unacknowledged_alerts': stats['unacknowledged_alerts'],
            'top_threats': threats[:5]  # Top 5 threats
        }

        return summary
