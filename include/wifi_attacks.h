/**
 * WiFi Attack Module
 * Provides WiFi-specific attack capabilities for security testing
 */

#ifndef WIFI_ATTACKS_H
#define WIFI_ATTACKS_H

#include "darknet.h"

/* WiFi frame types */
#define WIFI_FRAME_TYPE_MGMT 0x00
#define WIFI_FRAME_TYPE_CTRL 0x01
#define WIFI_FRAME_TYPE_DATA 0x02

/* Management frame subtypes */
#define WIFI_SUBTYPE_BEACON 0x08
#define WIFI_SUBTYPE_DEAUTH 0x0C
#define WIFI_SUBTYPE_AUTH 0x0B
#define WIFI_SUBTYPE_PROBE_REQ 0x04
#define WIFI_SUBTYPE_PROBE_RESP 0x05

/* WiFi network information */
typedef struct {
    mac_addr_t bssid;
    char ssid[33];
    int channel;
    int signal_strength;
    bool encrypted;
    char encryption_type[32];
} wifi_ap_t;

/* WiFi client information */
typedef struct {
    mac_addr_t mac;
    mac_addr_t ap_bssid;
    int signal_strength;
    uint64_t last_seen;
} wifi_client_t;

/* WiFi attack configuration */
typedef struct {
    network_interface_t *iface;
    mac_addr_t target_bssid;
    mac_addr_t target_client;
    int channel;
    int count;
    int delay_ms;
    bool broadcast;
} wifi_attack_config_t;

/* WiFi scanning */
int wifi_scan_networks(network_interface_t *iface, wifi_ap_t **aps, int *count, int timeout_sec);
int wifi_scan_clients(network_interface_t *iface, const mac_addr_t *bssid, wifi_client_t **clients, int *count, int timeout_sec);
int wifi_set_channel(network_interface_t *iface, int channel);

/* Deauthentication attacks */
int wifi_deauth_attack(const wifi_attack_config_t *config);
int wifi_deauth_broadcast(network_interface_t *iface, const mac_addr_t *bssid, int count);
int wifi_deauth_client(network_interface_t *iface, const mac_addr_t *bssid, const mac_addr_t *client, int count);

/* Evil twin / Rogue AP */
typedef struct {
    char ssid[33];
    mac_addr_t bssid;
    int channel;
    bool encryption;
    char auth_type[32];
} evil_twin_config_t;

int wifi_evil_twin_start(network_interface_t *iface, const evil_twin_config_t *config);
int wifi_evil_twin_stop(network_interface_t *iface);

/* Handshake capture */
typedef struct {
    mac_addr_t bssid;
    char ssid[33];
    uint8_t *handshake_data;
    size_t handshake_len;
    bool complete;
} wifi_handshake_t;

int wifi_capture_handshake(network_interface_t *iface, const mac_addr_t *bssid, wifi_handshake_t *handshake, int timeout_sec);
int wifi_save_handshake(const wifi_handshake_t *handshake, const char *filename);

/* WPS attacks */
int wifi_wps_pixie_dust(network_interface_t *iface, const mac_addr_t *bssid);
int wifi_wps_bruteforce(network_interface_t *iface, const mac_addr_t *bssid, const char *pin_file);

/* Beacon flooding */
int wifi_beacon_flood(network_interface_t *iface, int count, int channel);

/* Helper functions */
void wifi_mac_to_string(const mac_addr_t *mac, char *str, size_t len);
int wifi_string_to_mac(const char *str, mac_addr_t *mac);

#endif /* WIFI_ATTACKS_H */
