/**
 * Darknet - Core Framework Implementation
 */

#include "darknet.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/if_packet.h>
#include <linux/if_ether.h>

/* Global state */
static bool g_initialized = false;

/* Error messages */
static const char* error_messages[] = {
    [0] = "Success",
    [-DARKNET_ERROR] = "General error",
    [-DARKNET_ERROR_PERMISSION] = "Permission denied (requires root)",
    [-DARKNET_ERROR_INTERFACE] = "Network interface error",
    [-DARKNET_ERROR_INVALID_PARAM] = "Invalid parameter",
    [-DARKNET_ERROR_MEMORY] = "Memory allocation failed"
};

int darknet_init(void) {
    if (g_initialized) {
        return DARKNET_SUCCESS;
    }

    /* Check for root privileges */
    if (geteuid() != 0) {
        fprintf(stderr, "Error: Darknet requires root privileges\n");
        fprintf(stderr, "Please run with sudo or as root user\n");
        return DARKNET_ERROR_PERMISSION;
    }

    g_initialized = true;
    return DARKNET_SUCCESS;
}

void darknet_cleanup(void) {
    if (!g_initialized) {
        return;
    }

    g_initialized = false;
}

const char* darknet_version(void) {
    return DARKNET_VERSION;
}

const char* darknet_error_string(int error_code) {
    int idx = -error_code;
    if (idx >= 0 && idx < (int)(sizeof(error_messages) / sizeof(error_messages[0]))) {
        return error_messages[idx];
    }
    return "Unknown error";
}

/* Interface management */
int darknet_interface_open(const char *name, network_interface_t *iface) {
    if (!name || !iface) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    memset(iface, 0, sizeof(network_interface_t));
    strncpy(iface->name, name, MAX_INTERFACE_NAME - 1);

    /* Open raw socket */
    iface->fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (iface->fd < 0) {
        return DARKNET_ERROR_INTERFACE;
    }

    /* Get interface info */
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, name, IFNAMSIZ - 1);

    /* Get MAC address */
    if (ioctl(iface->fd, SIOCGIFHWADDR, &ifr) == 0) {
        memcpy(iface->mac.addr, ifr.ifr_hwaddr.sa_data, MAC_ADDR_LEN);
    }

    /* Get IP address */
    if (ioctl(iface->fd, SIOCGIFADDR, &ifr) == 0) {
        struct sockaddr_in *addr = (struct sockaddr_in *)&ifr.ifr_addr;
        memcpy(iface->ip.addr, &addr->sin_addr.s_addr, IPV4_ADDR_LEN);
    }

    return DARKNET_SUCCESS;
}

int darknet_interface_close(network_interface_t *iface) {
    if (!iface || iface->fd < 0) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    close(iface->fd);
    iface->fd = -1;
    return DARKNET_SUCCESS;
}

int darknet_interface_set_monitor_mode(network_interface_t *iface, bool enable) {
    if (!iface) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    /* This would require iwconfig/iw commands or nl80211 */
    /* Simplified implementation */
    iface->monitor_mode = enable;
    return DARKNET_SUCCESS;
}

int darknet_interface_list(char ***interfaces, int *count) {
    if (!interfaces || !count) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    /* This would enumerate network interfaces */
    /* Simplified stub */
    *count = 0;
    *interfaces = NULL;
    return DARKNET_SUCCESS;
}

/* Packet operations */
int darknet_packet_create(packet_t *pkt, size_t size) {
    if (!pkt || size == 0 || size > MAX_PACKET_SIZE) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    pkt->data = (uint8_t *)malloc(size);
    if (!pkt->data) {
        return DARKNET_ERROR_MEMORY;
    }

    pkt->len = size;
    pkt->timestamp = 0;
    memset(pkt->data, 0, size);

    return DARKNET_SUCCESS;
}

void darknet_packet_destroy(packet_t *pkt) {
    if (pkt && pkt->data) {
        free(pkt->data);
        pkt->data = NULL;
        pkt->len = 0;
    }
}

int darknet_packet_send(network_interface_t *iface, const packet_t *pkt) {
    if (!iface || !pkt || !pkt->data || pkt->len == 0) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    ssize_t sent = write(iface->fd, pkt->data, pkt->len);
    if (sent < 0 || (size_t)sent != pkt->len) {
        return DARKNET_ERROR;
    }

    return DARKNET_SUCCESS;
}

int darknet_packet_receive(network_interface_t *iface, packet_t *pkt, int timeout_ms) {
    if (!iface || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    /* Set socket timeout */
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    setsockopt(iface->fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    /* Receive packet */
    uint8_t buffer[MAX_PACKET_SIZE];
    ssize_t len = read(iface->fd, buffer, sizeof(buffer));

    if (len < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return DARKNET_ERROR; /* Timeout */
        }
        return DARKNET_ERROR;
    }

    /* Allocate and copy packet data */
    pkt->data = (uint8_t *)malloc(len);
    if (!pkt->data) {
        return DARKNET_ERROR_MEMORY;
    }

    memcpy(pkt->data, buffer, len);
    pkt->len = len;

    return DARKNET_SUCCESS;
}
