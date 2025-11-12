/**
 * Network Scanning Module
 * Provides comprehensive network reconnaissance capabilities
 */

#ifndef NETWORK_SCAN_H
#define NETWORK_SCAN_H

#include "darknet.h"

/* Port states */
typedef enum {
    PORT_OPEN,
    PORT_CLOSED,
    PORT_FILTERED,
    PORT_UNKNOWN
} port_state_t;

/* Scan types */
typedef enum {
    SCAN_TCP_CONNECT,
    SCAN_TCP_SYN,
    SCAN_TCP_FIN,
    SCAN_TCP_XMAS,
    SCAN_TCP_NULL,
    SCAN_UDP,
    SCAN_ACK
} scan_type_t;

/* Host information */
typedef struct {
    ipv4_addr_t ip;
    mac_addr_t mac;
    char hostname[256];
    bool alive;
    int latency_ms;
    char os_guess[128];
} host_info_t;

/* Port scan result */
typedef struct {
    uint16_t port;
    port_state_t state;
    char service[64];
    char version[128];
    char banner[256];
} port_scan_result_t;

/* Scan configuration */
typedef struct {
    ipv4_addr_t target_ip;
    char target_range[64];  /* CIDR notation */
    uint16_t *ports;
    int port_count;
    scan_type_t scan_type;
    int timeout_ms;
    int threads;
    bool service_detection;
    bool os_detection;
    bool aggressive;
} scan_config_t;

/* Host discovery */
int scan_ping_sweep(const char *network_range, host_info_t **hosts, int *count);
int scan_arp_discovery(network_interface_t *iface, const char *network_range, host_info_t **hosts, int *count);
int scan_check_host_alive(const ipv4_addr_t *ip, bool *alive, int timeout_ms);

/* Port scanning */
int scan_ports(const scan_config_t *config, port_scan_result_t **results, int *count);
int scan_single_port(const ipv4_addr_t *ip, uint16_t port, scan_type_t type, port_state_t *state);
int scan_tcp_connect(const ipv4_addr_t *ip, uint16_t port, port_state_t *state, int timeout_ms);
int scan_tcp_syn(const ipv4_addr_t *ip, uint16_t port, port_state_t *state, int timeout_ms);
int scan_udp(const ipv4_addr_t *ip, uint16_t port, port_state_t *state, int timeout_ms);

/* Service detection */
int scan_detect_service(const ipv4_addr_t *ip, uint16_t port, char *service, size_t service_len);
int scan_grab_banner(const ipv4_addr_t *ip, uint16_t port, char *banner, size_t banner_len, int timeout_ms);
int scan_service_version(const ipv4_addr_t *ip, uint16_t port, char *version, size_t version_len);

/* OS fingerprinting */
int scan_detect_os(const ipv4_addr_t *ip, char *os_info, size_t os_len);
int scan_tcp_fingerprint(const ipv4_addr_t *ip, char *os_info, size_t os_len);

/* Network mapping */
typedef struct {
    host_info_t *hosts;
    int host_count;
    char network_range[64];
    char gateway[64];
    char dns_servers[5][64];
    int dns_count;
} network_map_t;

int scan_map_network(const char *interface, network_map_t *map);
void scan_free_network_map(network_map_t *map);

/* Vulnerability detection */
typedef struct {
    char vuln_name[128];
    char cve_id[32];
    char severity[16];
    char description[512];
    ipv4_addr_t affected_host;
    uint16_t affected_port;
} vulnerability_t;

int scan_detect_vulnerabilities(const ipv4_addr_t *ip, vulnerability_t **vulns, int *count);

/* Traceroute */
typedef struct {
    int hop;
    ipv4_addr_t ip;
    char hostname[256];
    int rtt_ms;
} traceroute_hop_t;

int scan_traceroute(const ipv4_addr_t *target, traceroute_hop_t **hops, int *hop_count, int max_hops);

/* Helper functions */
int scan_parse_port_range(const char *range, uint16_t **ports, int *count);
void scan_ip_to_string(const ipv4_addr_t *ip, char *str, size_t len);
int scan_string_to_ip(const char *str, ipv4_addr_t *ip);

#endif /* NETWORK_SCAN_H */
