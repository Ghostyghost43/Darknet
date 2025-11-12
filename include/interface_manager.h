/**
 * Interface Manager Module
 * Manages network interfaces, monitor mode, and configuration
 */

#ifndef INTERFACE_MANAGER_H
#define INTERFACE_MANAGER_H

#include "darknet.h"

/* Interface types */
typedef enum {
    IFACE_TYPE_ETHERNET,
    IFACE_TYPE_WIRELESS,
    IFACE_TYPE_LOOPBACK,
    IFACE_TYPE_VPN,
    IFACE_TYPE_BRIDGE,
    IFACE_TYPE_UNKNOWN
} interface_type_t;

/* Interface state */
typedef enum {
    IFACE_STATE_UP,
    IFACE_STATE_DOWN,
    IFACE_STATE_DORMANT,
    IFACE_STATE_UNKNOWN
} interface_state_t;

/* Wireless modes */
typedef enum {
    WIRELESS_MODE_MANAGED,
    WIRELESS_MODE_MONITOR,
    WIRELESS_MODE_MASTER,
    WIRELESS_MODE_AD_HOC,
    WIRELESS_MODE_UNKNOWN
} wireless_mode_t;

/* Interface capabilities */
typedef struct {
    bool monitor_mode_support;
    bool packet_injection_support;
    bool promiscuous_mode;
    bool ap_mode_support;
    int max_tx_power;
    int supported_channels[64];
    int channel_count;
} interface_capabilities_t;

/* Interface statistics */
typedef struct {
    uint64_t rx_packets;
    uint64_t tx_packets;
    uint64_t rx_bytes;
    uint64_t tx_bytes;
    uint64_t rx_errors;
    uint64_t tx_errors;
    uint64_t rx_dropped;
    uint64_t tx_dropped;
} interface_stats_t;

/* Extended interface information */
typedef struct {
    char name[MAX_INTERFACE_NAME];
    char driver[64];
    char firmware_version[64];
    interface_type_t type;
    interface_state_t state;
    mac_addr_t mac;
    ipv4_addr_t ip;
    ipv4_addr_t netmask;
    ipv4_addr_t broadcast;
    ipv4_addr_t gateway;
    int mtu;
    wireless_mode_t wireless_mode;
    int current_channel;
    int tx_power;
    interface_capabilities_t capabilities;
    interface_stats_t stats;
} interface_info_t;

/* Interface configuration */
typedef struct {
    char name[MAX_INTERFACE_NAME];
    ipv4_addr_t ip;
    ipv4_addr_t netmask;
    ipv4_addr_t gateway;
    bool dhcp;
    int mtu;
    int channel;  /* For wireless */
    int tx_power;  /* For wireless */
    wireless_mode_t mode;  /* For wireless */
    bool promiscuous;
} interface_config_t;

/* Interface enumeration */
int iface_enumerate(interface_info_t **interfaces, int *count);
int iface_get_info(const char *name, interface_info_t *info);
int iface_get_type(const char *name, interface_type_t *type);
int iface_get_state(const char *name, interface_state_t *state);

/* Interface control */
int iface_up(const char *name);
int iface_down(const char *name);
int iface_restart(const char *name);
int iface_set_state(const char *name, interface_state_t state);

/* IP configuration */
int iface_set_ip(const char *name, const ipv4_addr_t *ip, const ipv4_addr_t *netmask);
int iface_set_gateway(const char *name, const ipv4_addr_t *gateway);
int iface_enable_dhcp(const char *name);
int iface_disable_dhcp(const char *name);
int iface_flush_ip(const char *name);

/* MAC address manipulation */
int iface_get_mac(const char *name, mac_addr_t *mac);
int iface_set_mac(const char *name, const mac_addr_t *mac);
int iface_randomize_mac(const char *name);
int iface_restore_mac(const char *name);

/* MTU configuration */
int iface_get_mtu(const char *name, int *mtu);
int iface_set_mtu(const char *name, int mtu);

/* Promiscuous mode */
int iface_enable_promiscuous(const char *name);
int iface_disable_promiscuous(const char *name);
int iface_is_promiscuous(const char *name, bool *enabled);

/* Wireless-specific functions */
int iface_is_wireless(const char *name, bool *wireless);
int iface_get_wireless_mode(const char *name, wireless_mode_t *mode);
int iface_set_wireless_mode(const char *name, wireless_mode_t mode);

/* Monitor mode management */
int iface_enable_monitor_mode(const char *name);
int iface_disable_monitor_mode(const char *name);
int iface_is_monitor_mode(const char *name, bool *enabled);
int iface_supports_monitor_mode(const char *name, bool *supported);

/* Channel management */
int iface_get_channel(const char *name, int *channel);
int iface_set_channel(const char *name, int channel);
int iface_get_supported_channels(const char *name, int *channels, int *count);
int iface_channel_hop_start(const char *name, int interval_ms);
int iface_channel_hop_stop(const char *name);

/* TX power management */
int iface_get_tx_power(const char *name, int *power_dbm);
int iface_set_tx_power(const char *name, int power_dbm);
int iface_get_max_tx_power(const char *name, int *max_power);

/* Packet injection support */
int iface_supports_injection(const char *name, bool *supported);
int iface_test_injection(const char *name, bool *working);

/* Statistics */
int iface_get_stats(const char *name, interface_stats_t *stats);
int iface_reset_stats(const char *name);
int iface_print_stats(const char *name);

/* Capabilities detection */
int iface_get_capabilities(const char *name, interface_capabilities_t *caps);
int iface_detect_driver(const char *name, char *driver, size_t len);
int iface_get_firmware_version(const char *name, char *version, size_t len);

/* Configuration management */
int iface_save_config(const char *name, const char *config_file);
int iface_load_config(const char *name, const char *config_file);
int iface_apply_config(const interface_config_t *config);

/* Interface creation/deletion */
int iface_create_virtual(const char *base_name, const char *new_name, interface_type_t type);
int iface_delete_virtual(const char *name);

/* Advanced features */
int iface_clone(const char *source, const char *dest);
int iface_bridge_create(const char *bridge_name, const char **interfaces, int count);
int iface_bridge_delete(const char *bridge_name);

/* Monitoring */
typedef void (*interface_event_callback_t)(const char *interface, const char *event, void *user_data);

int iface_monitor_start(interface_event_callback_t callback, void *user_data);
int iface_monitor_stop(void);

/* Utility functions */
const char* iface_type_to_string(interface_type_t type);
const char* iface_state_to_string(interface_state_t state);
const char* iface_wireless_mode_to_string(wireless_mode_t mode);
int iface_is_up(const char *name, bool *up);
int iface_find_wireless(char ***interfaces, int *count);
int iface_find_by_type(interface_type_t type, char ***interfaces, int *count);

#endif /* INTERFACE_MANAGER_H */
