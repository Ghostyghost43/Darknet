"""
Database module for tracking detected devices.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


class DeviceDatabase:
    """Manages SQLite database for device tracking."""

    def __init__(self, db_path: str = "data/devices.db"):
        """Initialize database connection."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac_address TEXT UNIQUE NOT NULL,
                    device_type TEXT NOT NULL,
                    vendor TEXT,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    times_seen INTEGER DEFAULT 1,
                    threat_level TEXT DEFAULT 'LOW',
                    notes TEXT
                )
            """)

            # Sightings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sightings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    signal_strength INTEGER,
                    location_context TEXT,
                    additional_data TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                )
            """)

            # WiFi specific data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wifi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    ssid TEXT,
                    channel INTEGER,
                    encryption TEXT,
                    last_updated TIMESTAMP NOT NULL,
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                )
            """)

            # Bluetooth specific data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bluetooth_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    device_name TEXT,
                    device_class TEXT,
                    last_updated TIMESTAMP NOT NULL,
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                )
            """)

            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    acknowledged BOOLEAN DEFAULT 0,
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                )
            """)

            conn.commit()

    def add_or_update_device(self, mac_address: str, device_type: str,
                            vendor: str = None) -> int:
        """Add a new device or update existing one."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            # Check if device exists
            cursor.execute(
                "SELECT id, times_seen FROM devices WHERE mac_address = ?",
                (mac_address,)
            )
            result = cursor.fetchone()

            if result:
                device_id = result[0]
                times_seen = result[1] + 1
                cursor.execute("""
                    UPDATE devices
                    SET last_seen = ?, times_seen = ?, vendor = COALESCE(?, vendor)
                    WHERE id = ?
                """, (now, times_seen, vendor, device_id))
            else:
                cursor.execute("""
                    INSERT INTO devices (mac_address, device_type, vendor,
                                       first_seen, last_seen, times_seen)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (mac_address, device_type, vendor, now, now))
                device_id = cursor.lastrowid

            return device_id

    def add_sighting(self, device_id: int, signal_strength: int = None,
                    location_context: str = None, additional_data: str = None):
        """Record a device sighting."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sightings
                (device_id, timestamp, signal_strength, location_context, additional_data)
                VALUES (?, ?, ?, ?, ?)
            """, (device_id, datetime.now().isoformat(), signal_strength,
                  location_context, additional_data))

    def add_wifi_data(self, device_id: int, ssid: str = None,
                     channel: int = None, encryption: str = None):
        """Add or update WiFi-specific data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute(
                "SELECT id FROM wifi_data WHERE device_id = ?",
                (device_id,)
            )
            result = cursor.fetchone()

            if result:
                cursor.execute("""
                    UPDATE wifi_data
                    SET ssid = COALESCE(?, ssid),
                        channel = COALESCE(?, channel),
                        encryption = COALESCE(?, encryption),
                        last_updated = ?
                    WHERE device_id = ?
                """, (ssid, channel, encryption, now, device_id))
            else:
                cursor.execute("""
                    INSERT INTO wifi_data
                    (device_id, ssid, channel, encryption, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (device_id, ssid, channel, encryption, now))

    def add_bluetooth_data(self, device_id: int, device_name: str = None,
                          device_class: str = None):
        """Add or update Bluetooth-specific data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute(
                "SELECT id FROM bluetooth_data WHERE device_id = ?",
                (device_id,)
            )
            result = cursor.fetchone()

            if result:
                cursor.execute("""
                    UPDATE bluetooth_data
                    SET device_name = COALESCE(?, device_name),
                        device_class = COALESCE(?, device_class),
                        last_updated = ?
                    WHERE device_id = ?
                """, (device_name, device_class, now, device_id))
            else:
                cursor.execute("""
                    INSERT INTO bluetooth_data
                    (device_id, device_name, device_class, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (device_id, device_name, device_class, now))

    def create_alert(self, device_id: int, alert_type: str, message: str):
        """Create an alert for a device."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (device_id, alert_type, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (device_id, alert_type, message, datetime.now().isoformat()))

    def get_device_by_mac(self, mac_address: str) -> Optional[Dict]:
        """Get device information by MAC address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM devices WHERE mac_address = ?",
                (mac_address,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_all_devices(self, limit: int = None) -> List[Dict]:
        """Get all tracked devices."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM devices ORDER BY last_seen DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_suspicious_devices(self, threshold: int = 3) -> List[Dict]:
        """Get devices seen multiple times (potentially tracking)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM devices
                WHERE times_seen >= ?
                ORDER BY times_seen DESC, last_seen DESC
            """, (threshold,))
            return [dict(row) for row in cursor.fetchall()]

    def get_device_sightings(self, device_id: int) -> List[Dict]:
        """Get all sightings for a specific device."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sightings
                WHERE device_id = ?
                ORDER BY timestamp DESC
            """, (device_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_alerts(self, limit: int = 10,
                         unacknowledged_only: bool = True) -> List[Dict]:
        """Get recent alerts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT a.*, d.mac_address, d.device_type, d.vendor
                FROM alerts a
                JOIN devices d ON a.device_id = d.id
            """
            if unacknowledged_only:
                query += " WHERE a.acknowledged = 0"
            query += f" ORDER BY a.timestamp DESC LIMIT {limit}"

            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def acknowledge_alert(self, alert_id: int):
        """Mark an alert as acknowledged."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE alerts SET acknowledged = 1 WHERE id = ?",
                (alert_id,)
            )

    def update_threat_level(self, device_id: int, threat_level: str):
        """Update device threat level."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE devices SET threat_level = ? WHERE id = ?",
                (threat_level, device_id)
            )

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT COUNT(*) as total FROM devices")
            stats['total_devices'] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) as total FROM devices WHERE device_type = 'WIFI'"
            )
            stats['wifi_devices'] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) as total FROM devices WHERE device_type = 'BLUETOOTH'"
            )
            stats['bluetooth_devices'] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) as total FROM devices WHERE times_seen >= 3"
            )
            stats['suspicious_devices'] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) as total FROM alerts WHERE acknowledged = 0"
            )
            stats['unacknowledged_alerts'] = cursor.fetchone()[0]

            return stats
