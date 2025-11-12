/**
 * Packet Crafting Module Implementation
 */

#include "darknet.h"
#include "packet_craft.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

/* Checksum calculation */
uint16_t packet_checksum(const uint8_t *data, size_t len) {
    uint32_t sum = 0;
    const uint16_t *ptr = (const uint16_t *)data;

    while (len > 1) {
        sum += *ptr++;
        len -= 2;
    }

    if (len > 0) {
        sum += *(uint8_t *)ptr;
    }

    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    return (uint16_t)~sum;
}

uint16_t packet_tcp_checksum(const ipv4_header_t *ip, const tcp_header_t *tcp, const uint8_t *payload, size_t payload_len) {
    /* TCP checksum includes pseudo-header */
    size_t total_len = sizeof(tcp_header_t) + payload_len;
    uint8_t *buffer = malloc(12 + total_len); /* Pseudo-header + TCP */
    if (!buffer) {
        return 0;
    }

    /* Build pseudo-header */
    memcpy(buffer, &ip->src_ip, 4);
    memcpy(buffer + 4, &ip->dst_ip, 4);
    buffer[8] = 0;
    buffer[9] = PROTO_TCP;
    *(uint16_t *)(buffer + 10) = htons(total_len);

    /* Copy TCP header and payload */
    memcpy(buffer + 12, tcp, sizeof(tcp_header_t));
    if (payload && payload_len > 0) {
        memcpy(buffer + 12 + sizeof(tcp_header_t), payload, payload_len);
    }

    uint16_t checksum = packet_checksum(buffer, 12 + total_len);
    free(buffer);
    return checksum;
}

uint16_t packet_udp_checksum(const ipv4_header_t *ip, const udp_header_t *udp, const uint8_t *payload, size_t payload_len) {
    /* UDP checksum also includes pseudo-header */
    size_t total_len = sizeof(udp_header_t) + payload_len;
    uint8_t *buffer = malloc(12 + total_len);
    if (!buffer) {
        return 0;
    }

    /* Build pseudo-header */
    memcpy(buffer, &ip->src_ip, 4);
    memcpy(buffer + 4, &ip->dst_ip, 4);
    buffer[8] = 0;
    buffer[9] = PROTO_UDP;
    *(uint16_t *)(buffer + 10) = htons(total_len);

    /* Copy UDP header and payload */
    memcpy(buffer + 12, udp, sizeof(udp_header_t));
    if (payload && payload_len > 0) {
        memcpy(buffer + 12 + sizeof(udp_header_t), payload, payload_len);
    }

    uint16_t checksum = packet_checksum(buffer, 12 + total_len);
    free(buffer);
    return checksum;
}

/* Packet building */
int packet_craft_ethernet(const mac_addr_t *src, const mac_addr_t *dst, uint16_t ethertype, packet_t *pkt) {
    if (!src || !dst || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    eth_header_t eth;
    memcpy(&eth.dst_mac, dst, sizeof(mac_addr_t));
    memcpy(&eth.src_mac, src, sizeof(mac_addr_t));
    eth.ethertype = htons(ethertype);

    int ret = darknet_packet_create(pkt, sizeof(eth_header_t));
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    memcpy(pkt->data, &eth, sizeof(eth_header_t));
    return DARKNET_SUCCESS;
}

int packet_craft_ipv4(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint8_t protocol, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!src || !dst || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    size_t total_len = sizeof(ipv4_header_t) + payload_len;
    int ret = darknet_packet_create(pkt, total_len);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    ipv4_header_t *ip = (ipv4_header_t *)pkt->data;
    ip->version_ihl = 0x45; /* Version 4, IHL 5 */
    ip->tos = 0;
    ip->total_length = htons(total_len);
    ip->id = htons(rand() & 0xFFFF);
    ip->flags_offset = 0;
    ip->ttl = 64;
    ip->protocol = protocol;
    ip->checksum = 0;
    memcpy(&ip->src_ip, src, sizeof(ipv4_addr_t));
    memcpy(&ip->dst_ip, dst, sizeof(ipv4_addr_t));

    ip->checksum = packet_checksum((uint8_t *)ip, sizeof(ipv4_header_t));

    if (payload && payload_len > 0) {
        memcpy(pkt->data + sizeof(ipv4_header_t), payload, payload_len);
    }

    return DARKNET_SUCCESS;
}

int packet_craft_tcp(uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, uint8_t flags, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    size_t total_len = sizeof(tcp_header_t) + payload_len;
    int ret = darknet_packet_create(pkt, total_len);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    tcp_header_t *tcp = (tcp_header_t *)pkt->data;
    tcp->src_port = htons(src_port);
    tcp->dst_port = htons(dst_port);
    tcp->seq_num = htonl(seq);
    tcp->ack_num = htonl(ack);
    tcp->data_offset_reserved = 0x50; /* Data offset 5 (20 bytes) */
    tcp->flags = flags;
    tcp->window = htons(65535);
    tcp->checksum = 0;
    tcp->urgent_ptr = 0;

    if (payload && payload_len > 0) {
        memcpy(pkt->data + sizeof(tcp_header_t), payload, payload_len);
    }

    return DARKNET_SUCCESS;
}

int packet_craft_udp(uint16_t src_port, uint16_t dst_port, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    size_t total_len = sizeof(udp_header_t) + payload_len;
    int ret = darknet_packet_create(pkt, total_len);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    udp_header_t *udp = (udp_header_t *)pkt->data;
    udp->src_port = htons(src_port);
    udp->dst_port = htons(dst_port);
    udp->length = htons(total_len);
    udp->checksum = 0;

    if (payload && payload_len > 0) {
        memcpy(pkt->data + sizeof(udp_header_t), payload, payload_len);
    }

    return DARKNET_SUCCESS;
}

int packet_craft_icmp(uint8_t type, uint8_t code, uint16_t id, uint16_t seq, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    size_t total_len = sizeof(icmp_header_t) + payload_len;
    int ret = darknet_packet_create(pkt, total_len);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    icmp_header_t *icmp = (icmp_header_t *)pkt->data;
    icmp->type = type;
    icmp->code = code;
    icmp->checksum = 0;
    icmp->id = htons(id);
    icmp->sequence = htons(seq);

    if (payload && payload_len > 0) {
        memcpy(pkt->data + sizeof(icmp_header_t), payload, payload_len);
    }

    icmp->checksum = packet_checksum(pkt->data, total_len);

    return DARKNET_SUCCESS;
}

/* Complete packet assembly */
int packet_craft_tcp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, uint8_t flags, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!src_ip || !dst_ip || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    /* Build TCP packet first */
    packet_t tcp_pkt;
    int ret = packet_craft_tcp(src_port, dst_port, seq, ack, flags, payload, payload_len, &tcp_pkt);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    /* Wrap in IP */
    ret = packet_craft_ipv4(src_ip, dst_ip, PROTO_TCP, tcp_pkt.data, tcp_pkt.len, pkt);
    darknet_packet_destroy(&tcp_pkt);

    return ret;
}

int packet_craft_udp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint16_t src_port, uint16_t dst_port, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!src_ip || !dst_ip || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    packet_t udp_pkt;
    int ret = packet_craft_udp(src_port, dst_port, payload, payload_len, &udp_pkt);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    ret = packet_craft_ipv4(src_ip, dst_ip, PROTO_UDP, udp_pkt.data, udp_pkt.len, pkt);
    darknet_packet_destroy(&udp_pkt);

    return ret;
}

int packet_craft_icmp_ip(const ipv4_addr_t *src_ip, const ipv4_addr_t *dst_ip, uint8_t type, uint8_t code, const uint8_t *payload, size_t payload_len, packet_t *pkt) {
    if (!src_ip || !dst_ip || !pkt) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    packet_t icmp_pkt;
    int ret = packet_craft_icmp(type, code, 0, 0, payload, payload_len, &icmp_pkt);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    ret = packet_craft_ipv4(src_ip, dst_ip, PROTO_ICMP, icmp_pkt.data, icmp_pkt.len, pkt);
    darknet_packet_destroy(&icmp_pkt);

    return ret;
}

/* Packet injection */
int packet_inject_raw(network_interface_t *iface, const packet_t *pkt) {
    return darknet_packet_send(iface, pkt);
}

int packet_inject_with_delay(network_interface_t *iface, const packet_t *pkt, int delay_ms) {
    usleep(delay_ms * 1000);
    return darknet_packet_send(iface, pkt);
}

int packet_inject_burst(network_interface_t *iface, const packet_t *pkt, int count, int interval_us) {
    for (int i = 0; i < count; i++) {
        darknet_packet_send(iface, pkt);
        if (i < count - 1) {
            usleep(interval_us);
        }
    }
    return DARKNET_SUCCESS;
}

/* Protocol-specific helpers */
int packet_tcp_handshake_syn(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, packet_t *pkt) {
    uint32_t seq = rand();
    return packet_craft_tcp_ip(src, dst, src_port, dst_port, seq, 0, TCP_FLAG_SYN, NULL, 0, pkt);
}

int packet_tcp_handshake_synack(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, packet_t *pkt) {
    return packet_craft_tcp_ip(src, dst, src_port, dst_port, seq, ack, TCP_FLAG_SYN | TCP_FLAG_ACK, NULL, 0, pkt);
}

int packet_tcp_handshake_ack(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, uint32_t ack, packet_t *pkt) {
    return packet_craft_tcp_ip(src, dst, src_port, dst_port, seq, ack, TCP_FLAG_ACK, NULL, 0, pkt);
}

int packet_tcp_reset(const ipv4_addr_t *src, const ipv4_addr_t *dst, uint16_t src_port, uint16_t dst_port, uint32_t seq, packet_t *pkt) {
    return packet_craft_tcp_ip(src, dst, src_port, dst_port, seq, 0, TCP_FLAG_RST, NULL, 0, pkt);
}

/* Utility functions */
void packet_hexdump(const packet_t *pkt) {
    if (!pkt || !pkt->data) {
        return;
    }

    printf("Packet dump (%zu bytes):\n", pkt->len);
    for (size_t i = 0; i < pkt->len; i++) {
        printf("%02x ", pkt->data[i]);
        if ((i + 1) % 16 == 0) {
            printf("\n");
        }
    }
    printf("\n");
}

int packet_copy(const packet_t *src, packet_t *dst) {
    if (!src || !dst) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    int ret = darknet_packet_create(dst, src->len);
    if (ret != DARKNET_SUCCESS) {
        return ret;
    }

    memcpy(dst->data, src->data, src->len);
    dst->timestamp = src->timestamp;

    return DARKNET_SUCCESS;
}

/* Packet sniffing stubs */
int packet_sniff_start(network_interface_t *iface, const sniff_config_t *config, packet_handler_t handler, void *user_data) {
    if (!iface || !config || !handler) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    printf("[Packet] Starting packet capture on %s\n", iface->name);
    if (config->filter[0]) {
        printf("[Packet] Filter: %s\n", config->filter);
    }

    return DARKNET_SUCCESS;
}

int packet_sniff_stop(network_interface_t *iface) {
    if (!iface) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    printf("[Packet] Stopping packet capture\n");
    return DARKNET_SUCCESS;
}

int packet_set_filter(network_interface_t *iface, const char *filter) {
    if (!iface || !filter) {
        return DARKNET_ERROR_INVALID_PARAM;
    }

    printf("[Packet] Setting BPF filter: %s\n", filter);
    return DARKNET_SUCCESS;
}
