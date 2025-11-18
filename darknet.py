#!/usr/bin/env python3
"""
Darknet - Counter-Intelligence Device Scanner
Main entry point
"""
import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config
from core.cli import CLI


def check_privileges():
    """Check if running with sufficient privileges."""
    if os.geteuid() != 0:
        print("\n⚠️  WARNING: Not running as root")
        print("Some features may not work without root privileges:")
        print("  • WiFi monitor mode (scapy)")
        print("  • Bluetooth scanning")
        print("\nFor full functionality, run with sudo:")
        print("  sudo ./darknet.py\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Darknet - Counter-Intelligence Device Scanner'
    )
    parser.add_argument(
        '-c', '--config',
        help='Configuration file path',
        default='config/default_config.yaml'
    )
    parser.add_argument(
        '--no-privilege-check',
        action='store_true',
        help='Skip privilege check'
    )

    args = parser.parse_args()

    # Check privileges
    if not args.no_privilege_check:
        check_privileges()

    # Load configuration
    config = Config(args.config)

    # Initialize and run CLI
    cli = CLI(config)
    cli.initialize_components()
    cli.run_interactive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
