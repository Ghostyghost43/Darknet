"""
Configuration management for Darknet framework
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class AttackConfig:
    """Attack configuration"""
    deauth_packets: int = 100
    deauth_reason: int = 7
    injection_rate: int = 100
    channel_hop: bool = True
    hop_interval: float = 0.5
    pmkid_timeout: int = 60
    handshake_timeout: int = 120
    aggressive_mode: bool = True
    auto_capture: bool = True


@dataclass
class DefenseConfig:
    """Defense configuration"""
    enable_ids: bool = True
    enable_deauth_detection: bool = True
    enable_rogue_ap_detection: bool = True
    enable_evil_twin_detection: bool = True
    alert_threshold: int = 10
    block_threats: bool = False
    auto_response: bool = False


@dataclass
class InterfaceConfig:
    """Interface configuration"""
    interface: Optional[str] = None
    monitor_mode: bool = True
    channel: int = 6
    mac_randomization: bool = True
    check_injection: bool = True


@dataclass
class NetworkConfig:
    """Network configuration"""
    gateway_ip: Optional[str] = None
    target_ip: Optional[str] = None
    mitm_enabled: bool = False
    dns_spoofing: bool = False
    arp_spoofing: bool = False
    ssl_strip: bool = False


@dataclass
class UIConfig:
    """UI configuration"""
    theme: str = "matrix"
    show_visualizations: bool = True
    interactive: bool = True
    verbose: bool = True
    color_output: bool = True
    animations: bool = True


@dataclass
class DarknetConfig:
    """Main Darknet configuration"""
    attack: AttackConfig = None
    defense: DefenseConfig = None
    interface: InterfaceConfig = None
    network: NetworkConfig = None
    ui: UIConfig = None

    def __post_init__(self):
        if self.attack is None:
            self.attack = AttackConfig()
        if self.defense is None:
            self.defense = DefenseConfig()
        if self.interface is None:
            self.interface = InterfaceConfig()
        if self.network is None:
            self.network = NetworkConfig()
        if self.ui is None:
            self.ui = UIConfig()

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'attack': asdict(self.attack),
            'defense': asdict(self.defense),
            'interface': asdict(self.interface),
            'network': asdict(self.network),
            'ui': asdict(self.ui)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DarknetConfig':
        """Create config from dictionary"""
        return cls(
            attack=AttackConfig(**data.get('attack', {})),
            defense=DefenseConfig(**data.get('defense', {})),
            interface=InterfaceConfig(**data.get('interface', {})),
            network=NetworkConfig(**data.get('network', {})),
            ui=UIConfig(**data.get('ui', {}))
        )

    def save(self, filepath: str):
        """Save configuration to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def load(cls, filepath: str) -> 'DarknetConfig':
        """Load configuration from file"""
        if not os.path.exists(filepath):
            return cls()

        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)


# Default config instance
default_config = DarknetConfig()
