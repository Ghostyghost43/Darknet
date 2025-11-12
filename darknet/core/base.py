"""
Base classes for Darknet modules
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
import threading
from darknet.utils.constants import *
from darknet.utils.logger import setup_logger


class ModuleStatus(Enum):
    """Module status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class BaseModule(ABC):
    """Base class for all Darknet modules"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = ModuleStatus.IDLE
        self.logger = setup_logger(name)
        self._stop_event = threading.Event()
        self._thread = None
        self.results = {}
        self.errors = []

    @abstractmethod
    def setup(self, **kwargs) -> bool:
        """
        Setup the module with provided configuration
        Returns: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the module
        Returns: Dictionary containing results
        """
        pass

    @abstractmethod
    def stop(self):
        """Stop the module execution"""
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources used by the module"""
        pass

    def start(self) -> bool:
        """Start the module in a separate thread"""
        if self.status == ModuleStatus.RUNNING:
            self.logger.warning(f"{self.name} is already running")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_wrapper)
        self._thread.daemon = True
        self._thread.start()
        return True

    def _run_wrapper(self):
        """Wrapper for run method to handle status and errors"""
        try:
            self.status = ModuleStatus.RUNNING
            self.logger.info(f"Starting {self.name}")
            self.results = self.run()
            self.status = ModuleStatus.STOPPED
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.errors.append(str(e))
            self.logger.error(f"Error in {self.name}: {str(e)}")

    def is_running(self) -> bool:
        """Check if module is running"""
        return self.status == ModuleStatus.RUNNING

    def get_status(self) -> str:
        """Get current module status"""
        return self.status.value

    def get_results(self) -> Dict[str, Any]:
        """Get module results"""
        return self.results

    def get_errors(self) -> list:
        """Get module errors"""
        return self.errors

    def pause(self):
        """Pause module execution"""
        if self.status == ModuleStatus.RUNNING:
            self.status = ModuleStatus.PAUSED
            self.logger.info(f"{self.name} paused")

    def resume(self):
        """Resume module execution"""
        if self.status == ModuleStatus.PAUSED:
            self.status = ModuleStatus.RUNNING
            self.logger.info(f"{self.name} resumed")


class AttackModule(BaseModule):
    """Base class for attack modules"""

    def __init__(self, name: str, description: str, attack_type: str):
        super().__init__(name, description)
        self.attack_type = attack_type
        self.target = None
        self.interface = None
        self.packets_sent = 0
        self.success_count = 0
        self.failure_count = 0

    def set_target(self, target: Any):
        """Set attack target"""
        self.target = target
        self.logger.info(f"Target set: {target}")

    def set_interface(self, interface: str):
        """Set network interface"""
        self.interface = interface
        self.logger.info(f"Interface set: {interface}")

    def get_statistics(self) -> Dict[str, int]:
        """Get attack statistics"""
        return {
            'packets_sent': self.packets_sent,
            'success_count': self.success_count,
            'failure_count': self.failure_count
        }


class DefenseModule(BaseModule):
    """Base class for defense modules"""

    def __init__(self, name: str, description: str, detection_type: str):
        super().__init__(name, description)
        self.detection_type = detection_type
        self.interface = None
        self.threats_detected = []
        self.alerts_raised = 0
        self.blocked_count = 0

    def set_interface(self, interface: str):
        """Set network interface for monitoring"""
        self.interface = interface
        self.logger.info(f"Monitoring interface: {interface}")

    def add_threat(self, threat: Dict[str, Any]):
        """Add detected threat"""
        self.threats_detected.append(threat)
        self.alerts_raised += 1
        self.logger.warning(f"Threat detected: {threat.get('type', 'Unknown')}")

    def get_threats(self) -> list:
        """Get detected threats"""
        return self.threats_detected

    def get_statistics(self) -> Dict[str, int]:
        """Get defense statistics"""
        return {
            'threats_detected': len(self.threats_detected),
            'alerts_raised': self.alerts_raised,
            'blocked_count': self.blocked_count
        }

    @abstractmethod
    def analyze_packet(self, packet: Any) -> Optional[Dict[str, Any]]:
        """
        Analyze packet for threats
        Returns: Threat dictionary if threat detected, None otherwise
        """
        pass
