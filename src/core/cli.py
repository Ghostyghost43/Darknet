"""
Interactive CLI for the device scanning tool.
"""
import os
import sys
import time
import signal
from datetime import datetime
from typing import Optional
from tabulate import tabulate

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback if colorama not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''


class CLI:
    """Interactive command-line interface."""

    def __init__(self, config):
        """Initialize CLI."""
        self.config = config
        self.running = False
        self.db = None
        self.wifi_scanner = None
        self.bt_scanner = None
        self.pattern_detector = None

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
        self.running = False
        sys.exit(0)

    def initialize_components(self):
        """Initialize scanner and database components."""
        from ..core.database import DeviceDatabase
        from ..scanners.wifi_scanner import WiFiScanner
        from ..scanners.bluetooth_scanner import BluetoothScanner
        from ..core.pattern_detector import PatternDetector

        print(f"{Fore.CYAN}Initializing components...{Style.RESET_ALL}")

        self.db = DeviceDatabase(self.config.get('db_path', 'data/devices.db'))
        self.wifi_scanner = WiFiScanner(self.config.get('wifi_interface'))
        self.bt_scanner = BluetoothScanner(self.config.get('bt_adapter', 'hci0'))
        self.pattern_detector = PatternDetector(self.db)

        print(f"{Fore.GREEN}✓ Components initialized{Style.RESET_ALL}")

    def print_banner(self):
        """Print application banner."""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  {Fore.RED}█████{Fore.CYAN}╗ {Fore.RED}████{Fore.CYAN}╗{Fore.RED}███████{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}╗  {Fore.RED}██{Fore.CYAN}╗{Fore.RED}███{Fore.CYAN}╗   {Fore.RED}██{Fore.CYAN}╗{Fore.RED}███████{Fore.CYAN}╗{Fore.RED}████████{Fore.CYAN}╗  ║
║  {Fore.RED}██{Fore.CYAN}╔══{Fore.RED}██{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}╔══{Fore.RED}██{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}╔════╝{Fore.RED}██{Fore.CYAN}║ {Fore.RED}██{Fore.CYAN}╔╝{Fore.RED}████{Fore.CYAN}╗  {Fore.RED}██{Fore.CYAN}║{Fore.RED}██{Fore.CYAN}╔════╝╚══{Fore.RED}██{Fore.CYAN}╔══╝  ║
║  {Fore.RED}██{Fore.CYAN}║  {Fore.RED}██{Fore.CYAN}║{Fore.RED}███████{Fore.CYAN}║{Fore.RED}██{Fore.CYAN}║     {Fore.RED}█████{Fore.CYAN}╔╝ {Fore.RED}██{Fore.CYAN}╔{Fore.RED}██{Fore.CYAN}╗ {Fore.RED}██{Fore.CYAN}║{Fore.RED}█████{Fore.CYAN}╗     {Fore.RED}██{Fore.CYAN}║     ║
║  {Fore.RED}██{Fore.CYAN}║  {Fore.RED}██{Fore.CYAN}║{Fore.RED}██{Fore.CYAN}╔══{Fore.RED}██{Fore.CYAN}║{Fore.RED}██{Fore.CYAN}║     {Fore.RED}██{Fore.CYAN}╔═{Fore.RED}██{Fore.CYAN}╗ {Fore.RED}██{Fore.CYAN}║╚{Fore.RED}██{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}║{Fore.RED}██{Fore.CYAN}╔══╝     {Fore.RED}██{Fore.CYAN}║     ║
║  {Fore.RED}█████{Fore.CYAN}╔╝{Fore.RED}██{Fore.CYAN}║  {Fore.RED}██{Fore.CYAN}║{Fore.RED}███████{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}║  {Fore.RED}██{Fore.CYAN}╗{Fore.RED}██{Fore.CYAN}║ ╚{Fore.RED}████{Fore.CYAN}║{Fore.RED}███████{Fore.CYAN}╗   {Fore.RED}██{Fore.CYAN}║     ║
║  ╚════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝     ║
║                                                              ║
║         {Fore.YELLOW}Counter-Intelligence Device Scanner{Fore.CYAN}              ║
║              {Fore.WHITE}Detect. Track. Stay Safe.{Fore.CYAN}                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)

    def print_help(self):
        """Print help information."""
        help_text = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║  COMMANDS                                                    ║
╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}

  {Fore.GREEN}scan{Style.RESET_ALL}              - Run a single scan (WiFi + Bluetooth)
  {Fore.GREEN}scan wifi{Style.RESET_ALL}         - Scan WiFi only
  {Fore.GREEN}scan bluetooth{Style.RESET_ALL}    - Scan Bluetooth only
  {Fore.GREEN}monitor{Style.RESET_ALL}           - Start continuous monitoring

  {Fore.YELLOW}list{Style.RESET_ALL}              - List all detected devices
  {Fore.YELLOW}threats{Style.RESET_ALL}           - Show threat analysis
  {Fore.YELLOW}alerts{Style.RESET_ALL}            - Show recent alerts
  {Fore.YELLOW}stats{Style.RESET_ALL}             - Show statistics

  {Fore.MAGENTA}device <mac>{Style.RESET_ALL}     - Show detailed device information
  {Fore.MAGENTA}analyze <mac>{Style.RESET_ALL}    - Analyze device for threats
  {Fore.MAGENTA}note <mac> <text>{Style.RESET_ALL} - Add note to device

  {Fore.CYAN}export{Style.RESET_ALL}            - Export data to file
  {Fore.CYAN}clear{Style.RESET_ALL}             - Clear screen
  {Fore.CYAN}help{Style.RESET_ALL}              - Show this help
  {Fore.RED}exit{Style.RESET_ALL}              - Exit program

{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(help_text)

    def cmd_scan(self, args):
        """Run a scan."""
        scan_type = args[0] if args else 'all'

        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Starting scan: {scan_type.upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        devices_found = 0

        # WiFi scan
        if scan_type in ['all', 'wifi']:
            print(f"{Fore.CYAN}[*] Scanning WiFi...{Style.RESET_ALL}")
            try:
                wifi_devices = self.wifi_scanner.scan(
                    method=self.config.get('wifi_scan_method', 'auto'),
                    duration=self.config.get('wifi_scan_duration', 10)
                )

                for device in wifi_devices:
                    device_id = self.db.add_or_update_device(
                        device['mac'], 'WIFI', device.get('vendor')
                    )
                    self.db.add_sighting(device_id, device.get('signal_strength'))

                    if device.get('ssid'):
                        self.db.add_wifi_data(
                            device_id, device['ssid'],
                            device.get('channel'), device.get('encryption')
                        )

                    # Check for threats
                    self.pattern_detector.check_and_create_alerts(device_id)

                devices_found += len(wifi_devices)
                print(f"{Fore.GREEN}✓ WiFi scan complete: {len(wifi_devices)} devices found{Style.RESET_ALL}\n")

            except Exception as e:
                print(f"{Fore.RED}✗ WiFi scan error: {e}{Style.RESET_ALL}\n")

        # Bluetooth scan
        if scan_type in ['all', 'bluetooth', 'bt']:
            print(f"{Fore.CYAN}[*] Scanning Bluetooth...{Style.RESET_ALL}")
            try:
                bt_devices = self.bt_scanner.scan(
                    duration=self.config.get('bt_scan_duration', 10)
                )

                for device in bt_devices:
                    device_id = self.db.add_or_update_device(
                        device['mac'], 'BLUETOOTH', None
                    )
                    self.db.add_sighting(device_id, device.get('signal_strength'))

                    self.db.add_bluetooth_data(
                        device_id, device.get('name'), device.get('device_class')
                    )

                    # Check for threats
                    alerts = self.pattern_detector.check_and_create_alerts(device_id)
                    if alerts and device.get('is_tracker'):
                        print(f"{Fore.RED}  [!!! TRACKER ALERT !!!] {device['mac']} - {device['name']}{Style.RESET_ALL}")

                devices_found += len(bt_devices)
                print(f"{Fore.GREEN}✓ Bluetooth scan complete: {len(bt_devices)} devices found{Style.RESET_ALL}\n")

            except Exception as e:
                print(f"{Fore.RED}✗ Bluetooth scan error: {e}{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Scan complete: {devices_found} total devices found{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        # Show any critical alerts
        self._show_critical_alerts()

    def cmd_monitor(self, args):
        """Start continuous monitoring."""
        interval = self.config.get('scan_interval', 60)

        print(f"\n{Fore.YELLOW}Starting continuous monitoring...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Scan interval: {interval} seconds{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Press Ctrl+C to stop{Style.RESET_ALL}\n")

        self.running = True
        scan_count = 0

        try:
            while self.running:
                scan_count += 1
                print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Scan #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

                self.cmd_scan(['all'])

                if self.running:
                    print(f"{Fore.CYAN}Next scan in {interval} seconds...{Style.RESET_ALL}\n")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped{Style.RESET_ALL}\n")
            self.running = False

    def cmd_list(self, args):
        """List all detected devices."""
        devices = self.db.get_all_devices(limit=50)

        if not devices:
            print(f"\n{Fore.YELLOW}No devices found. Run a scan first.{Style.RESET_ALL}\n")
            return

        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Detected Devices ({len(devices)}){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        table_data = []
        for device in devices[:50]:
            threat_color = {
                'CRITICAL': Fore.RED,
                'HIGH': Fore.RED,
                'MEDIUM': Fore.YELLOW,
                'LOW': Fore.GREEN
            }.get(device['threat_level'], Fore.WHITE)

            table_data.append([
                device['mac_address'],
                device['device_type'],
                device['vendor'] or 'Unknown',
                device['times_seen'],
                f"{threat_color}{device['threat_level']}{Style.RESET_ALL}",
                device['last_seen'][:16]
            ])

        headers = ['MAC Address', 'Type', 'Vendor', 'Seen', 'Threat', 'Last Seen']
        print(tabulate(table_data, headers=headers, tablefmt='simple'))
        print()

    def cmd_threats(self, args):
        """Show threat analysis."""
        threats = self.pattern_detector.scan_all_devices_for_threats()

        if not threats:
            print(f"\n{Fore.GREEN}No significant threats detected{Style.RESET_ALL}\n")
            return

        print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.RED}THREAT ANALYSIS - {len(threats)} Suspicious Devices{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")

        for threat in threats:
            device = threat['device']
            threat_color = {
                'CRITICAL': Fore.RED + Style.BRIGHT,
                'HIGH': Fore.RED,
                'MEDIUM': Fore.YELLOW
            }.get(threat['threat_level'], Fore.WHITE)

            print(f"{threat_color}[{threat['threat_level']}] {device['mac_address']}{Style.RESET_ALL}")
            print(f"  Type: {device['device_type']} | Vendor: {device['vendor'] or 'Unknown'}")
            print(f"  Seen: {device['times_seen']} times | Last: {device['last_seen'][:16]}")
            print(f"  Threat Score: {threat['threat_score']}")

            if threat['suspicious_patterns']:
                print(f"  {Fore.YELLOW}Suspicious Patterns:{Style.RESET_ALL}")
                for pattern in threat['suspicious_patterns']:
                    print(f"    • [{pattern['severity']}] {pattern['description']}")

            if threat['recommendations']:
                print(f"  {Fore.CYAN}Recommendations:{Style.RESET_ALL}")
                for rec in threat['recommendations'][:3]:
                    print(f"    → {rec}")

            print()

    def cmd_alerts(self, args):
        """Show recent alerts."""
        alerts = self.db.get_recent_alerts(limit=20)

        if not alerts:
            print(f"\n{Fore.GREEN}No alerts{Style.RESET_ALL}\n")
            return

        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Recent Alerts ({len(alerts)}){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

        for alert in alerts:
            print(f"{Fore.RED}[{alert['alert_type']}] {alert['mac_address']}{Style.RESET_ALL}")
            print(f"  {alert['message']}")
            print(f"  Time: {alert['timestamp'][:19]}")
            print()

    def cmd_stats(self, args):
        """Show statistics."""
        summary = self.pattern_detector.get_threat_summary()

        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}STATISTICS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        print(f"  Total Devices Tracked:     {summary['total_devices']}")
        print(f"  WiFi Devices:              {summary['wifi_devices']}")
        print(f"  Bluetooth Devices:         {summary['bluetooth_devices']}")
        print(f"\n  {Fore.YELLOW}Threat Summary:{Style.RESET_ALL}")
        print(f"    {Fore.RED}Critical Threats:        {summary['critical_threats']}{Style.RESET_ALL}")
        print(f"    {Fore.RED}High Threats:            {summary['high_threats']}{Style.RESET_ALL}")
        print(f"    {Fore.YELLOW}Medium Threats:          {summary['medium_threats']}{Style.RESET_ALL}")
        print(f"\n  Unacknowledged Alerts:     {summary['unacknowledged_alerts']}")
        print()

    def cmd_device(self, args):
        """Show device details."""
        if not args:
            print(f"{Fore.RED}Usage: device <mac_address>{Style.RESET_ALL}\n")
            return

        mac = args[0].upper()
        device = self.db.get_device_by_mac(mac)

        if not device:
            print(f"{Fore.RED}Device not found: {mac}{Style.RESET_ALL}\n")
            return

        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}DEVICE DETAILS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        threat_color = {
            'CRITICAL': Fore.RED + Style.BRIGHT,
            'HIGH': Fore.RED,
            'MEDIUM': Fore.YELLOW,
            'LOW': Fore.GREEN
        }.get(device['threat_level'], Fore.WHITE)

        print(f"  MAC Address:       {device['mac_address']}")
        print(f"  Device Type:       {device['device_type']}")
        print(f"  Vendor:            {device['vendor'] or 'Unknown'}")
        print(f"  First Seen:        {device['first_seen']}")
        print(f"  Last Seen:         {device['last_seen']}")
        print(f"  Times Seen:        {device['times_seen']}")
        print(f"  Threat Level:      {threat_color}{device['threat_level']}{Style.RESET_ALL}")

        # Get sightings
        sightings = self.db.get_device_sightings(device['id'])
        print(f"\n  Recent Sightings ({len(sightings)}):")
        for sighting in sightings[:10]:
            print(f"    • {sighting['timestamp'][:19]}", end='')
            if sighting.get('location_context'):
                print(f" - {sighting['location_context']}", end='')
            if sighting.get('signal_strength'):
                print(f" (Signal: {sighting['signal_strength']})", end='')
            print()

        print()

    def _show_critical_alerts(self):
        """Show critical alerts."""
        alerts = self.db.get_recent_alerts(limit=5, unacknowledged_only=True)
        critical = [a for a in alerts if 'CRITICAL' in a['alert_type']]

        if critical:
            print(f"\n{Fore.RED + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.RED + Style.BRIGHT}!!! CRITICAL ALERTS !!!{Style.RESET_ALL}")
            print(f"{Fore.RED + Style.BRIGHT}{'='*60}{Style.RESET_ALL}\n")

            for alert in critical:
                print(f"{Fore.RED}[{alert['alert_type']}] {alert['mac_address']}{Style.RESET_ALL}")
                print(f"  {alert['message']}\n")

    def run_interactive(self):
        """Run interactive CLI."""
        self.print_banner()
        print(f"{Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}\n")

        while True:
            try:
                command = input(f"{Fore.GREEN}darknet>{Style.RESET_ALL} ").strip().lower()

                if not command:
                    continue

                parts = command.split()
                cmd = parts[0]
                args = parts[1:]

                if cmd in ['exit', 'quit', 'q']:
                    print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                    break
                elif cmd == 'help':
                    self.print_help()
                elif cmd == 'scan':
                    self.cmd_scan(args)
                elif cmd == 'monitor':
                    self.cmd_monitor(args)
                elif cmd == 'list':
                    self.cmd_list(args)
                elif cmd == 'threats':
                    self.cmd_threats(args)
                elif cmd == 'alerts':
                    self.cmd_alerts(args)
                elif cmd == 'stats':
                    self.cmd_stats(args)
                elif cmd == 'device':
                    self.cmd_device(args)
                elif cmd == 'clear':
                    os.system('clear' if os.name != 'nt' else 'cls')
                else:
                    print(f"{Fore.RED}Unknown command: {cmd}{Style.RESET_ALL}")
                    print(f"Type 'help' for available commands\n")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Use 'exit' to quit{Style.RESET_ALL}\n")
                continue
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")
