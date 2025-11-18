"""
Configuration management for Darknet scanner.
"""
import os
import yaml
from typing import Dict, Any


class Config:
    """Configuration manager."""

    def __init__(self, config_file: str = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self._load_default_config()

        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'db_path': 'data/devices.db',
            'wifi_interface': None,
            'wifi_scan_method': 'auto',
            'wifi_scan_duration': 10,
            'bt_adapter': 'hci0',
            'bt_scan_duration': 10,
            'bt_scan_types': ['classic', 'ble'],
            'scan_interval': 60,
            'enable_auto_alerts': True,
            'threat_thresholds': {
                'low': 2,
                'medium': 4,
                'high': 7,
                'critical': 11
            },
            'enable_location_context': True,
            'default_location': 'unknown',
            'log_level': 'INFO',
            'log_file': 'logs/darknet.log'
        }

    def _load_config_file(self, config_file: str):
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self.config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value

    def save(self, config_file: str):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
