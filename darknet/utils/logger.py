"""
Logging system for Darknet framework
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.logging import RichHandler

console = Console()


class DarknetLogger:
    """Custom logger for Darknet framework"""

    def __init__(self, name: str = "darknet", log_file: Optional[str] = None, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation
        if log_file is None:
            log_file = log_dir / f"darknet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        else:
            log_file = log_dir / log_file

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler with rich formatting
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def success(self, message: str):
        """Log success message"""
        console.print(f"[bold green]✓[/bold green] {message}")
        self.logger.info(f"SUCCESS: {message}")

    def attack(self, message: str):
        """Log attack message"""
        console.print(f"[bold red]⚡[/bold red] {message}")
        self.logger.info(f"ATTACK: {message}")

    def defense(self, message: str):
        """Log defense message"""
        console.print(f"[bold blue]🛡[/bold blue] {message}")
        self.logger.info(f"DEFENSE: {message}")

    def capture(self, message: str):
        """Log capture message"""
        console.print(f"[bold yellow]📡[/bold yellow] {message}")
        self.logger.info(f"CAPTURE: {message}")


def setup_logger(name: str = "darknet", log_file: Optional[str] = None, level: int = logging.INFO) -> DarknetLogger:
    """Setup and return a logger instance"""
    return DarknetLogger(name, log_file, level)
