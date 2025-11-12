"""
Darknet CLI - Main command-line interface
Matrix-themed interface for the Darknet wireless security framework
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from darknet.utils.logger import setup_logger
from darknet.utils.helpers import is_root, get_wireless_interfaces
from darknet.network.interface import InterfaceManager
from darknet.network.scanner import WirelessScanner
from darknet.offensive.deauth import DeauthAttack
from darknet.offensive.evil_twin import EvilTwinAttack
from darknet.offensive.pmkid import PMKIDAttack
from darknet.offensive.handshake import HandshakeCapture
from darknet.offensive.beacon_flood import BeaconFloodAttack
from darknet.offensive.auth_flood import AuthFloodAttack
from darknet.mitm.arp_spoof import ARPSpoof
from darknet.mitm.dns_spoof import DNSSpoof
from darknet.mitm.sniffer import PacketSniffer
from darknet.defensive.ids import WirelessIDS
import sys

console = Console()
logger = setup_logger()


def print_banner():
    """Print Matrix-themed banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║  ██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗  ║
║  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝  ║
║  ██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║     ║
║  ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║     ║
║  ██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║     ║
║  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝     ║
║                                                                 ║
║        Advanced Wireless Security Framework v1.0.0             ║
║        Red Team + Blue Team + MITM Capabilities                ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold green")
    console.print("\n[bold yellow]WARNING:[/] For authorized security testing only!\n", style="blink")


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Darknet - Advanced Wireless Security Framework"""
    print_banner()

    if not is_root():
        console.print("[bold red]ERROR:[/] This tool requires root privileges!", style="bold red")
        console.print("Run with: sudo darknet <command>")
        sys.exit(1)


@cli.command()
def interfaces():
    """List wireless interfaces"""
    console.print("\n[bold green]Scanning for wireless interfaces...[/]\n")

    iface_mgr = InterfaceManager()
    interfaces = iface_mgr.list_interfaces()

    if not interfaces:
        console.print("[bold red]No wireless interfaces found![/]")
        return

    table = Table(title="Wireless Interfaces", box=box.ROUNDED, style="green")
    table.add_column("Interface", style="cyan")
    table.add_column("Mode", style="magenta")
    table.add_column("MAC Address", style="yellow")
    table.add_column("Monitor Support", style="blue")

    for iface in interfaces:
        info = iface_mgr.get_interface_info(iface)
        table.add_row(
            iface,
            info.get('mode', 'Unknown'),
            info.get('mac', 'Unknown'),
            "✓" if info.get('monitor_support') else "✗"
        )

    console.print(table)


@cli.command()
@click.option('-i', '--interface', required=True, help='Wireless interface')
@click.option('-d', '--duration', default=30, help='Scan duration in seconds')
@click.option('--channel-hop/--no-channel-hop', default=True, help='Enable channel hopping')
def scan(interface, duration, channel_hop):
    """Scan for wireless networks"""
    console.print(f"\n[bold green]Scanning for wireless networks on {interface}...[/]\n")

    # Setup interface
    iface_mgr = InterfaceManager()
    if not iface_mgr.enable_monitor_mode(interface):
        console.print("[bold red]Failed to enable monitor mode![/]")
        return

    # Create scanner
    scanner = WirelessScanner()
    if not scanner.setup(
        interface=interface,
        scan_duration=duration,
        channel_hop=channel_hop
    ):
        console.print("[bold red]Failed to setup scanner![/]")
        return

    # Run scan
    scanner.start()

    # Wait for completion
    import time
    time.sleep(duration + 2)

    # Get results
    aps = scanner.get_access_points()

    # Display results
    table = Table(title=f"Discovered Networks ({len(aps)} APs)", box=box.DOUBLE, style="green")
    table.add_column("SSID", style="cyan")
    table.add_column("BSSID", style="yellow")
    table.add_column("Channel", style="magenta")
    table.add_column("Encryption", style="red")
    table.add_column("Signal", style="blue")
    table.add_column("Clients", style="green")

    for ap in aps:
        table.add_row(
            ap.ssid or "<Hidden>",
            ap.mac,
            str(ap.channel) if ap.channel else "?",
            ap.encryption,
            f"{ap.signal_strength} dBm",
            str(ap.get_client_count())
        )

    console.print(table)


@cli.command()
@click.option('-i', '--interface', required=True, help='Wireless interface')
@click.option('-a', '--ap-mac', required=True, help='Target AP MAC address')
@click.option('-c', '--client-mac', help='Target client MAC (omit for broadcast)')
@click.option('-n', '--count', default=100, help='Number of packets')
@click.option('-r', '--rate', default=200, help='Packets per second')
def deauth(interface, ap_mac, client_mac, count, rate):
    """Deauthentication attack"""
    console.print(f"\n[bold red]⚡ Launching deauth attack on {ap_mac}...[/]\n")

    # Setup interface
    iface_mgr = InterfaceManager()
    if not iface_mgr.configure_for_attacks(interface):
        return

    # Create attack
    attack = DeauthAttack()
    if not attack.setup(
        interface=interface,
        ap_mac=ap_mac,
        client_mac=client_mac,
        packet_count=count,
        injection_rate=rate
    ):
        return

    # Execute attack
    attack.start()
    console.print("\n[bold green]✓ Attack completed![/]")


@cli.command()
@click.option('-i', '--interface', required=True, help='Wireless interface')
@click.option('-s', '--ssid', required=True, help='Target SSID')
@click.option('-a', '--ap-mac', required=True, help='Target AP MAC')
@click.option('-c', '--channel', default=6, help='Channel')
def evil_twin(interface, ssid, ap_mac, channel):
    """Evil twin attack"""
    console.print(f"\n[bold red]👿 Creating evil twin for {ssid}...[/]\n")

    attack = EvilTwinAttack()
    if not attack.setup(
        interface=interface,
        target_ssid=ssid,
        target_mac=ap_mac,
        target_channel=channel
    ):
        return

    console.print("[bold yellow]Evil twin AP is running. Press Ctrl+C to stop...[/]")
    attack.start()


@cli.command()
@click.option('-i', '--interface', required=True, help='Network interface')
@click.option('-t', '--target', required=True, help='Target IP address')
@click.option('-g', '--gateway', required=True, help='Gateway IP address')
def arp_spoof(interface, target, gateway):
    """ARP spoofing attack"""
    console.print(f"\n[bold red]🎭 Starting ARP spoofing: {target} <-> {gateway}...[/]\n")

    attack = ARPSpoof()
    if not attack.setup(
        interface=interface,
        target_ip=target,
        gateway_ip=gateway
    ):
        return

    console.print("[bold yellow]ARP spoofing active. Press Ctrl+C to stop...[/]")
    attack.start()


@cli.command()
@click.option('-i', '--interface', required=True, help='Network interface')
@click.option('-d', '--domain', help='Domain to spoof')
@click.option('-ip', '--spoof-ip', help='IP address to respond with')
@click.option('--wildcard', is_flag=True, help='Spoof all domains')
def dns_spoof(interface, domain, spoof_ip, wildcard):
    """DNS spoofing attack"""
    console.print(f"\n[bold red]🌐 Starting DNS spoofing...[/]\n")

    attack = DNSSpoof()
    if not attack.setup(
        interface=interface,
        target_domain=domain,
        spoof_ip=spoof_ip,
        wildcard=wildcard
    ):
        return

    console.print("[bold yellow]DNS spoofing active. Press Ctrl+C to stop...[/]")
    attack.start()


@cli.command()
@click.option('-i', '--interface', required=True, help='Network interface')
@click.option('--passwords/--no-passwords', default=True, help='Capture passwords')
@click.option('--cookies/--no-cookies', default=True, help='Capture cookies')
@click.option('--urls/--no-urls', default=True, help='Capture URLs')
def sniff(interface, passwords, cookies, urls):
    """Packet sniffing"""
    console.print(f"\n[bold green]📡 Starting packet sniffer on {interface}...[/]\n")

    sniffer = PacketSniffer()
    if not sniffer.setup(
        interface=interface,
        capture_passwords=passwords,
        capture_cookies=cookies,
        capture_urls=urls
    ):
        return

    console.print("[bold yellow]Sniffing network traffic. Press Ctrl+C to stop...[/]")
    sniffer.start()


@cli.command()
@click.option('-i', '--interface', required=True, help='Wireless interface')
@click.option('--deauth-threshold', default=10, help='Deauth packets per minute')
@click.option('--beacon-threshold', default=100, help='Beacons per minute')
def ids(interface, deauth_threshold, beacon_threshold):
    """Wireless Intrusion Detection System"""
    console.print(f"\n[bold blue]🛡 Starting Wireless IDS on {interface}...[/]\n")

    # Setup interface
    iface_mgr = InterfaceManager()
    if not iface_mgr.enable_monitor_mode(interface):
        return

    ids_system = WirelessIDS()
    if not ids_system.setup(
        interface=interface,
        deauth_threshold=deauth_threshold,
        beacon_threshold=beacon_threshold
    ):
        return

    console.print("[bold green]IDS is monitoring. Press Ctrl+C to stop...[/]")
    ids_system.start()


@cli.command()
def console_mode():
    """Start interactive console (Metasploit-style)"""
    console.print("\n[bold green]Starting interactive console...[/]")
    console.print("[bold yellow]Feature coming soon![/]")


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Interrupted by user. Exiting...[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
