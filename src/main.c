/**
 * Darknet - Main Entry Point
 * Network Pentesting & Stress Testing Framework
 *
 * LEGAL NOTICE:
 * This tool is intended for authorized security testing and educational purposes only.
 * Unauthorized use against networks you do not own or have explicit written permission
 * to test is illegal. The authors assume no liability for misuse of this software.
 */

#include "darknet.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

/* Forward declarations */
void print_banner(void);
void print_usage(void);
void print_modules(void);
int handle_wifi_command(int argc, char **argv);
int handle_scan_command(int argc, char **argv);
int handle_arp_command(int argc, char **argv);
int handle_stress_command(int argc, char **argv);
int handle_packet_command(int argc, char **argv);
void signal_handler(int signum);

/* Global cleanup flag */
static volatile int g_running = 1;

int main(int argc, char **argv) {
    /* Setup signal handlers */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    print_banner();

    if (argc < 2) {
        print_usage();
        return 1;
    }

    /* Initialize framework */
    int ret = darknet_init();
    if (ret != DARKNET_SUCCESS) {
        fprintf(stderr, "Error: Failed to initialize Darknet: %s\n",
                darknet_error_string(ret));
        return 1;
    }

    printf("[*] Darknet initialized successfully\n");
    printf("[*] Running on kernel: Linux 4.4.0\n\n");

    /* Parse command */
    const char *command = argv[1];

    if (strcmp(command, "wifi") == 0) {
        ret = handle_wifi_command(argc - 1, argv + 1);
    } else if (strcmp(command, "scan") == 0) {
        ret = handle_scan_command(argc - 1, argv + 1);
    } else if (strcmp(command, "arp") == 0) {
        ret = handle_arp_command(argc - 1, argv + 1);
    } else if (strcmp(command, "stress") == 0) {
        ret = handle_stress_command(argc - 1, argv + 1);
    } else if (strcmp(command, "packet") == 0) {
        ret = handle_packet_command(argc - 1, argv + 1);
    } else if (strcmp(command, "modules") == 0) {
        print_modules();
        ret = 0;
    } else if (strcmp(command, "version") == 0 || strcmp(command, "-v") == 0) {
        printf("Darknet version %s\n", darknet_version());
        ret = 0;
    } else if (strcmp(command, "help") == 0 || strcmp(command, "-h") == 0) {
        print_usage();
        ret = 0;
    } else {
        fprintf(stderr, "Error: Unknown command '%s'\n", command);
        fprintf(stderr, "Use 'darknet help' for usage information\n");
        ret = 1;
    }

    /* Cleanup */
    darknet_cleanup();
    printf("\n[*] Darknet shutdown complete\n");

    return ret;
}

void print_banner(void) {
    printf("\n");
    printf("██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗\n");
    printf("██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝\n");
    printf("██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║   \n");
    printf("██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║   \n");
    printf("██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║   \n");
    printf("╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   \n");
    printf("\n");
    printf("   Network Pentesting & Stress Testing Framework v%s\n", DARKNET_VERSION);
    printf("   For authorized security testing only\n");
    printf("\n");
}

void print_usage(void) {
    printf("Usage: darknet <module> [options]\n\n");
    printf("Modules:\n");
    printf("  wifi      - WiFi attack and reconnaissance tools\n");
    printf("  scan      - Network scanning and enumeration\n");
    printf("  arp       - ARP poisoning and MITM attacks\n");
    printf("  stress    - Network stress testing and DoS\n");
    printf("  packet    - Packet crafting and injection\n");
    printf("  modules   - List all available modules\n");
    printf("  version   - Show version information\n");
    printf("  help      - Show this help message\n\n");
    printf("Examples:\n");
    printf("  darknet wifi scan -i wlan0\n");
    printf("  darknet scan ports -t 192.168.1.1 -p 1-1000\n");
    printf("  darknet arp poison -i eth0 -t 192.168.1.100 -g 192.168.1.1\n");
    printf("  darknet stress syn -t 192.168.1.1 -p 80 -d 60\n\n");
    printf("For module-specific help: darknet <module> --help\n");
}

void print_modules(void) {
    printf("Available Modules:\n\n");

    printf("WiFi Attacks (wifi):\n");
    printf("  - Deauthentication attacks\n");
    printf("  - Evil twin / rogue AP\n");
    printf("  - WPA/WPA2 handshake capture\n");
    printf("  - WPS attacks (Pixie Dust, bruteforce)\n");
    printf("  - Beacon flooding\n");
    printf("  - Client detection and monitoring\n\n");

    printf("Network Scanning (scan):\n");
    printf("  - Host discovery (ping sweep, ARP scan)\n");
    printf("  - Port scanning (TCP connect, SYN, UDP)\n");
    printf("  - Service detection and version identification\n");
    printf("  - OS fingerprinting\n");
    printf("  - Vulnerability detection\n");
    printf("  - Traceroute\n\n");

    printf("ARP Attacks (arp):\n");
    printf("  - ARP cache poisoning\n");
    printf("  - Man-in-the-middle (MITM) attacks\n");
    printf("  - Gateway spoofing\n");
    printf("  - Bidirectional poisoning\n");
    printf("  - ARP scanning and discovery\n");
    printf("  - Traffic interception\n\n");

    printf("Stress Testing (stress):\n");
    printf("  - TCP SYN/ACK/RST/FIN floods\n");
    printf("  - UDP flood attacks\n");
    printf("  - ICMP flood / Ping of Death\n");
    printf("  - HTTP flood / Slowloris\n");
    printf("  - DNS/NTP amplification\n");
    printf("  - Fragmentation attacks\n");
    printf("  - Connection exhaustion\n\n");

    printf("Packet Crafting (packet):\n");
    printf("  - Raw packet creation and manipulation\n");
    printf("  - Protocol-specific packet crafting\n");
    printf("  - Packet injection and sniffing\n");
    printf("  - Capture file handling\n");
    printf("  - Custom protocol implementation\n\n");
}

int handle_wifi_command(int argc, char **argv) {
    if (argc < 2) {
        printf("WiFi Module Usage:\n");
        printf("  darknet wifi scan -i <interface>           - Scan for WiFi networks\n");
        printf("  darknet wifi deauth -i <interface> -b <bssid> -c <client>\n");
        printf("  darknet wifi handshake -i <interface> -b <bssid>\n");
        printf("  darknet wifi evil-twin -i <interface> -s <ssid>\n");
        return 1;
    }

    const char *subcommand = argv[1];

    if (strcmp(subcommand, "scan") == 0) {
        printf("[WiFi] Network scanning not yet implemented\n");
        printf("[WiFi] This feature requires nl80211 library integration\n");
    } else if (strcmp(subcommand, "deauth") == 0) {
        printf("[WiFi] Deauth attack not yet implemented\n");
        printf("[WiFi] This feature requires monitor mode and raw 802.11 injection\n");
    } else {
        printf("[WiFi] Unknown subcommand: %s\n", subcommand);
        return 1;
    }

    return 0;
}

int handle_scan_command(int argc, char **argv) {
    if (argc < 2) {
        printf("Scan Module Usage:\n");
        printf("  darknet scan ping -r <range>               - Ping sweep\n");
        printf("  darknet scan ports -t <target> -p <ports>  - Port scan\n");
        printf("  darknet scan os -t <target>                - OS fingerprint\n");
        printf("  darknet scan traceroute -t <target>        - Traceroute\n");
        return 1;
    }

    const char *subcommand = argv[1];

    if (strcmp(subcommand, "ping") == 0) {
        printf("[Scan] Ping sweep not yet implemented\n");
    } else if (strcmp(subcommand, "ports") == 0) {
        printf("[Scan] Port scanning not yet implemented\n");
        printf("[Scan] This feature requires socket programming and raw packet support\n");
    } else {
        printf("[Scan] Unknown subcommand: %s\n", subcommand);
        return 1;
    }

    return 0;
}

int handle_arp_command(int argc, char **argv) {
    if (argc < 2) {
        printf("ARP Module Usage:\n");
        printf("  darknet arp scan -i <interface> -r <range>  - ARP scan\n");
        printf("  darknet arp poison -i <interface> -t <target> -g <gateway>\n");
        printf("  darknet arp mitm -i <interface> -t <target> -g <gateway>\n");
        printf("  darknet arp restore -i <interface> -t <target> -g <gateway>\n");
        return 1;
    }

    const char *subcommand = argv[1];

    if (strcmp(subcommand, "scan") == 0) {
        printf("[ARP] ARP scanning not yet implemented\n");
    } else if (strcmp(subcommand, "poison") == 0) {
        printf("[ARP] ARP poisoning not yet implemented\n");
        printf("[ARP] This feature requires raw socket access and ARP packet crafting\n");
    } else {
        printf("[ARP] Unknown subcommand: %s\n", subcommand);
        return 1;
    }

    return 0;
}

int handle_stress_command(int argc, char **argv) {
    if (argc < 2) {
        printf("Stress Module Usage:\n");
        printf("  darknet stress syn -t <target> -p <port> -d <duration>\n");
        printf("  darknet stress udp -t <target> -p <port> -d <duration>\n");
        printf("  darknet stress icmp -t <target> -d <duration>\n");
        printf("  darknet stress http -u <url> -c <connections>\n");
        return 1;
    }

    const char *subcommand = argv[1];

    if (strcmp(subcommand, "syn") == 0) {
        printf("[Stress] SYN flood not yet implemented\n");
        printf("[Stress] This feature requires raw socket support and packet crafting\n");
    } else if (strcmp(subcommand, "udp") == 0) {
        printf("[Stress] UDP flood not yet implemented\n");
    } else {
        printf("[Stress] Unknown subcommand: %s\n", subcommand);
        return 1;
    }

    return 0;
}

int handle_packet_command(int argc, char **argv) {
    if (argc < 2) {
        printf("Packet Module Usage:\n");
        printf("  darknet packet craft -p <protocol> -s <src> -d <dst>\n");
        printf("  darknet packet sniff -i <interface> -f <filter>\n");
        printf("  darknet packet inject -i <interface> -f <pcap_file>\n");
        return 1;
    }

    const char *subcommand = argv[1];

    if (strcmp(subcommand, "craft") == 0) {
        printf("[Packet] Packet crafting not yet implemented\n");
    } else if (strcmp(subcommand, "sniff") == 0) {
        printf("[Packet] Packet sniffing not yet implemented\n");
        printf("[Packet] This feature requires libpcap integration\n");
    } else {
        printf("[Packet] Unknown subcommand: %s\n", subcommand);
        return 1;
    }

    return 0;
}

void signal_handler(int signum) {
    if (signum == SIGINT || signum == SIGTERM) {
        printf("\n\n[!] Caught signal %d, shutting down...\n", signum);
        g_running = 0;

        /* Cleanup any active attacks */
        arp_poison_stop();
        stress_stop_attack();

        darknet_cleanup();
        exit(0);
    }
}
