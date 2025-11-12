/**
 * Darknet - Network Pentesting & Stress Testing Framework
 *
 * LEGAL NOTICE:
 * This tool is designed for authorized security testing and educational purposes only.
 * Unauthorized use against networks you don't own or have explicit permission to test
 * is illegal and punishable by law. Use responsibly.
 */

#ifndef DARKNET_H
#define DARKNET_H

#include <stdint.h>
#include <stdbool.h>
#include <sys/types.h>

#define DARKNET_VERSION "1.0.0"
#define MAX_INTERFACE_NAME 16
#define MAX_PACKET_SIZE 2048
#define MAC_ADDR_LEN 6
#define IPV4_ADDR_LEN 4

/* Return codes */
#define DARKNET_SUCCESS 0
#define DARKNET_ERROR -1
#define DARKNET_ERROR_PERMISSION -2
#define DARKNET_ERROR_INTERFACE -3
#define DARKNET_ERROR_INVALID_PARAM -4
#define DARKNET_ERROR_MEMORY -5

/* Structure definitions */
typedef struct {
    uint8_t addr[MAC_ADDR_LEN];
} mac_addr_t;

typedef struct {
    uint8_t addr[IPV4_ADDR_LEN];
} ipv4_addr_t;

typedef struct {
    char name[MAX_INTERFACE_NAME];
    int fd;
    bool monitor_mode;
    mac_addr_t mac;
    ipv4_addr_t ip;
} network_interface_t;

typedef struct {
    uint8_t *data;
    size_t len;
    uint64_t timestamp;
} packet_t;

/* Core framework functions */
int darknet_init(void);
void darknet_cleanup(void);
const char* darknet_version(void);
const char* darknet_error_string(int error_code);

/* Interface management */
int darknet_interface_open(const char *name, network_interface_t *iface);
int darknet_interface_close(network_interface_t *iface);
int darknet_interface_set_monitor_mode(network_interface_t *iface, bool enable);
int darknet_interface_list(char ***interfaces, int *count);

/* Packet operations */
int darknet_packet_create(packet_t *pkt, size_t size);
void darknet_packet_destroy(packet_t *pkt);
int darknet_packet_send(network_interface_t *iface, const packet_t *pkt);
int darknet_packet_receive(network_interface_t *iface, packet_t *pkt, int timeout_ms);

/* Module headers */
#include "wifi_attacks.h"
#include "network_scan.h"
#include "arp_attacks.h"
#include "stress_test.h"
#include "packet_craft.h"

#endif /* DARKNET_H */
