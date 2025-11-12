/**
 * Packet Crafting Module
 * Low-level packet creation and manipulation
 */

#ifndef PACKET_CRAFT_H
#define PACKET_CRAFT_H

#include "darknet.h"

/* Protocol numbers */
#define PROTO_ICMP 1
#define PROTO_TCP 6
#define PROTO_UDP 17

/* TCP flags */
#define TCP_FLAG_FIN 0x01
#define TCP_FLAG_SYN 0x02
#define TCP_FLAG_RST 0x04
#define TCP_FLAG_PSH 0x08
#define TCP_FLAG_ACK 0x10
#define TCP_FLAG_URG 0x20
#define TCP_FLAG_ECE 0x40
#define TCP_FLAG_CWR 0x80

/* ICMP types */
#define ICMP_ECHO_REPLY 0
#define ICMP_DEST_UNREACH 3
#define ICMP_ECHO_REQUEST 8
#define ICMP_TIME_EXCEEDED 11

/* Ethernet header */
typedef struct {
    mac_addr_t dst_mac;
    mac_addr_t src_mac;
    uint16_t ethertype;
} eth_header_t;

/* IPv4 header */
typedef struct {
    uint8_t version_ihl;
    uint8_t tos;
    uint16_t total_length;
    uint16_t id;
    uint16_t flags_offset;
    uint8_t ttl;
    uint8_t protocol;
    uint16_t checksum;
    ipv4_addr_t src_ip;
    ipv4_addr_t dst_ip;
} ipv4_header_t;

/* TCP header */
typedef struct {
    uint16_t src_port;
    uint16_t dst_port;
    uint32_t seq_num;
    uint32_t ack_num;
    uint8_t data_offset_reserved;
    uint8_t flags;
    uint16_t window;
    uint16_t checksum;
    uint16_t urgent_ptr;
} tcp_header_t;

/* UDP header */
typedef struct {
    uint16_t src_port;
    uint16_t dst_port;
    uint16_t length;
    uint16_t checksum;
} udp_header_t;

/* ICMP header */
typedef struct {
    uint8_t type;
    uint8_t code;
    uint16_t checksum;
    uint16_t id;
    uint16_t sequence;
} icmp_header_t;

/* DNS header */
typedef struct {
    uint16_t id;
    uint16_t flags;
    uint16_t questions;
    uint16_t answers;
    uint16_t authority;
    uint16_t additional;
} dns_header_t;

/* Packet building */
int packet_craft_ethernet(const mac_addr_t *src, const mac_addr_t *dst, uint16_t ethertype, packet_t *pkt);
int packet_craft_ipv4(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint8_t protocol, const uint8_t *payload, size_t payload_len, packet_t *pkt);
int packet_craft_tcp(uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, uint8_t flags, const uint8_t *payload, size_t payload_len, packet_t *pkt);
int packet_craft_udp(uint16_t src_port, uint16_t dst_port, const uint8_t *payload, size_t payload_len, packet_t *pkt);
int packet_craft_icmp(uint8_t type, uint8_t code, uint16_t id, uint16_t seq, const uint8_t *payload, size_t payload_len, packet_t *pkt);

/* Complete packet assembly */
int packet_craft_tcp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, uint8_t flags, const uint8_t *payload, size_t payload_len, packet_t *pkt);
int packet_craft_udp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint16_t src_port, uint16_t dst_port, const uint8_t *payload, size_t payload_len, packet_t *pkt);
int packet_craft_icmp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint8_t type, uint8_t code, const uint8_t *payload, size_t payload_len, packet_t *pkt);

/* Full stack with ethernet */
int packet_craft_full_tcp(const mac_addr_t *src_mac, const mac_addr_t *dst_mac, const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, uint8_t flags, const uint8_t *payload, size_t payload_len, packet_t *pkt);

/* Packet parsing */
int packet_parse_ethernet(const packet_t *pkt, eth_header_t *eth);
int packet_parse_ipv4(const packet_t *pkt, ipv4_header_t *ip);
int packet_parse_tcp(const packet_t *pkt, tcp_header_t *tcp);
int packet_parse_udp(const packet_t *pkt, udp_header_t *udp);
int packet_parse_icmp(const packet_t *pkt, icmp_header_t *icmp);

/* Checksum calculation */
uint16_t packet_checksum(const uint8_t *data, size_t len);
uint16_t packet_tcp_checksum(const ipv4_header_t *ip, const tcp_header_t *tcp, const uint8_t *payload, size_t payload_len);
uint16_t packet_udp_checksum(const ipv4_header_t *ip, const udp_header_t *udp, const uint8_t *payload, size_t payload_len);

/* Packet modification */
int packet_set_src_ip(packet_t *pkt, const ipv4_addr_t *ip);
int packet_set_dst_ip(packet_t *pkt, const ipv4_addr_t *ip);
int packet_set_src_port(packet_t *pkt, uint16_t port);
int packet_set_dst_port(packet_t *pkt, uint16_t port);
int packet_set_tcp_flags(packet_t *pkt, uint8_t flags);
int packet_set_ttl(packet_t *pkt, uint8_t ttl);

/* Packet injection */
int packet_inject_raw(network_interface_t *iface, const packet_t *pkt);
int packet_inject_with_delay(network_interface_t *iface, const packet_t *pkt, int delay_ms);
int packet_inject_burst(network_interface_t *iface, const packet_t *pkt, int count, int interval_us);

/* Packet sniffing */
typedef void (*packet_handler_t)(const packet_t *pkt, void *user_data);

typedef struct {
    char filter[256];  /* BPF filter expression */
    int snaplen;
    int timeout_ms;
    bool promiscuous;
} sniff_config_t;

int packet_sniff_start(network_interface_t *iface, const sniff_config_t *config, packet_handler_t handler, void *user_data);
int packet_sniff_stop(network_interface_t *iface);
int packet_set_filter(network_interface_t *iface, const char *filter);

/* Packet capture */
int packet_capture_to_file(network_interface_t *iface, const char *filename, int packet_count, int timeout_sec);
int packet_read_from_file(const char *filename, packet_t **packets, int *count);

/* Protocol-specific helpers */
int packet_tcp_handshake_syn(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, packet_t *pkt);
int packet_tcp_handshake_synack(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, packet_t *pkt);
int packet_tcp_handshake_ack(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, packet_t *pkt);
int packet_tcp_reset(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, packet_t *pkt);

/* DNS packet crafting */
int packet_craft_dns_query(const char *domain, uint16_t query_type, packet_t *pkt);
int packet_craft_dns_response(const char *domain, const ipv4_addr_t *answer, packet_t *pkt);

/* HTTP packet crafting */
int packet_craft_http_get(const char *host, const char *path, packet_t *pkt);
int packet_craft_http_post(const char *host, const char *path, const char *data, size_t data_len, packet_t *pkt);

/* Utility functions */
void packet_hexdump(const packet_t *pkt);
int packet_to_string(const packet_t *pkt, char *str, size_t len);
int packet_copy(const packet_t *src, packet_t *dst);

#endif /* PACKET_CRAFT_H */
