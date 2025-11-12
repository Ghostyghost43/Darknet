/**
 * ARP Attack Module
 * Provides ARP poisoning and MITM capabilities
 */

#ifndef ARP_ATTACKS_H
#define ARP_ATTACKS_H

#include "darknet.h"

/* ARP operations */
#define ARP_OP_REQUEST 1
#define ARP_OP_REPLY 2

/* ARP packet structure */
typedef struct {
    mac_addr_t sender_mac;
    ipv4_addr_t sender_ip;
    mac_addr_t target_mac;
    ipv4_addr_t target_ip;
    uint16_t operation;
} arp_packet_t;

/* ARP cache entry */
typedef struct {
    ipv4_addr_t ip;
    mac_addr_t mac;
    char interface[MAX_INTERFACE_NAME];
    bool static_entry;
    uint64_t timestamp;
} arp_cache_entry_t;

/* ARP poisoning configuration */
typedef struct {
    network_interface_t *iface;
    ipv4_addr_t target_ip;
    ipv4_addr_t gateway_ip;
    mac_addr_t attacker_mac;
    int interval_ms;
    bool bidirectional;
    bool restore_on_exit;
} arp_poison_config_t;

/* ARP cache operations */
int arp_get_cache(arp_cache_entry_t **entries, int *count);
int arp_add_cache_entry(const ipv4_addr_t *ip, const mac_addr_t *mac, const char *interface);
int arp_delete_cache_entry(const ipv4_addr_t *ip);
int arp_flush_cache(void);

/* ARP scanning */
int arp_scan_network(network_interface_t *iface, const char *network_range, arp_cache_entry_t **entries, int *count);
int arp_resolve_ip(network_interface_t *iface, const ipv4_addr_t *ip, mac_addr_t *mac, int timeout_ms);
int arp_who_has(network_interface_t *iface, const ipv4_addr_t *target_ip, arp_cache_entry_t *entry);

/* ARP poisoning attacks */
int arp_poison_start(const arp_poison_config_t *config);
int arp_poison_stop(void);
int arp_poison_single(network_interface_t *iface, const ipv4_addr_t *target_ip, const ipv4_addr_t *spoof_ip, const mac_addr_t *attacker_mac);
int arp_poison_bidirectional(network_interface_t *iface, const ipv4_addr_t *target1, const ipv4_addr_t *target2, const mac_addr_t *attacker_mac);

/* Gateway spoofing */
int arp_spoof_gateway(network_interface_t *iface, const ipv4_addr_t *target_ip, const ipv4_addr_t *gateway_ip, const mac_addr_t *attacker_mac);
int arp_mitm_attack(network_interface_t *iface, const ipv4_addr_t *victim_ip, const ipv4_addr_t *gateway_ip);

/* ARP restoration */
int arp_restore_target(network_interface_t *iface, const ipv4_addr_t *target_ip, const ipv4_addr_t *gateway_ip, const mac_addr_t *real_gateway_mac);
int arp_restore_all_targets(void);

/* ARP packet crafting */
int arp_craft_request(const ipv4_addr_t *sender_ip, const mac_addr_t *sender_mac, const ipv4_addr_t *target_ip, packet_t *pkt);
int arp_craft_reply(const ipv4_addr_t *sender_ip, const mac_addr_t *sender_mac, const ipv4_addr_t *target_ip, const mac_addr_t *target_mac, packet_t *pkt);
int arp_craft_gratuitous(const ipv4_addr_t *ip, const mac_addr_t *mac, packet_t *pkt);

/* Traffic interception */
typedef void (*packet_callback_t)(const packet_t *pkt, void *user_data);

int arp_intercept_traffic(network_interface_t *iface, packet_callback_t callback, void *user_data);
int arp_forward_packet(network_interface_t *iface, const packet_t *pkt, const mac_addr_t *dst_mac);

/* MITM helpers */
int arp_enable_ip_forwarding(void);
int arp_disable_ip_forwarding(void);
int arp_setup_iptables_forward(const char *interface);
int arp_cleanup_iptables_forward(const char *interface);

/* Detection and defense */
int arp_detect_poisoning(network_interface_t *iface, bool *detected);
int arp_monitor_anomalies(network_interface_t *iface, int duration_sec);

#endif /* ARP_ATTACKS_H */
