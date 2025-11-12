/**
 * Data Export Module
 * Handles data storage, export, and format conversion
 */

#ifndef DATA_EXPORT_H
#define DATA_EXPORT_H

#include "darknet.h"
#include "wifi_attacks.h"
#include "network_scan.h"
#include <time.h>

/* Export formats */
typedef enum {
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_CSV,
    EXPORT_FORMAT_XML,
    EXPORT_FORMAT_HTML,
    EXPORT_FORMAT_PCAP,
    EXPORT_FORMAT_TXT
} export_format_t;

/* Data categories */
typedef enum {
    DATA_CATEGORY_WIFI_SCAN,
    DATA_CATEGORY_PORT_SCAN,
    DATA_CATEGORY_VULNERABILITIES,
    DATA_CATEGORY_NETWORK_MAP,
    DATA_CATEGORY_ATTACK_RESULTS,
    DATA_CATEGORY_PACKETS,
    DATA_CATEGORY_ALL
} data_category_t;

/* Session information */
typedef struct {
    char session_id[64];
    time_t start_time;
    time_t end_time;
    char operator_name[128];
    char target_description[256];
    int total_hosts;
    int total_vulnerabilities;
    int total_packets;
} session_info_t;

/* WiFi scan export data */
typedef struct {
    wifi_ap_t *access_points;
    int ap_count;
    wifi_client_t *clients;
    int client_count;
    time_t scan_time;
    char interface[MAX_INTERFACE_NAME];
} wifi_scan_export_t;

/* Port scan export data */
typedef struct {
    host_info_t *hosts;
    int host_count;
    port_scan_result_t *ports;
    int port_count;
    time_t scan_time;
    char scan_type[32];
} port_scan_export_t;

/* Vulnerability export data */
typedef struct {
    vulnerability_t *vulnerabilities;
    int vuln_count;
    time_t scan_time;
    int critical_count;
    int high_count;
    int medium_count;
    int low_count;
} vulnerability_export_t;

/* Export configuration */
typedef struct {
    export_format_t format;
    data_category_t category;
    char output_dir[256];
    char filename[128];
    bool include_timestamp;
    bool compress;
    bool encrypt;
    char encryption_key[64];
} export_config_t;

/* Session management */
int export_session_create(session_info_t *session);
int export_session_update(const session_info_t *session);
int export_session_close(const char *session_id);
int export_session_load(const char *session_id, session_info_t *session);

/* WiFi data export */
int export_wifi_scan_json(const wifi_scan_export_t *data, const char *filename);
int export_wifi_scan_csv(const wifi_scan_export_t *data, const char *filename);
int export_wifi_scan_html(const wifi_scan_export_t *data, const char *filename);

/* Port scan export */
int export_port_scan_json(const port_scan_export_t *data, const char *filename);
int export_port_scan_csv(const port_scan_export_t *data, const char *filename);
int export_port_scan_xml(const port_scan_export_t *data, const char *filename);

/* Vulnerability export */
int export_vulnerabilities_json(const vulnerability_export_t *data, const char *filename);
int export_vulnerabilities_csv(const vulnerability_export_t *data, const char *filename);
int export_vulnerabilities_html(const vulnerability_export_t *data, const char *filename);

/* Packet capture export */
int export_packets_pcap(const packet_t *packets, int count, const char *filename);
int export_packets_json(const packet_t *packets, int count, const char *filename);

/* Network map export */
int export_network_map_json(const network_map_t *map, const char *filename);
int export_network_map_graphviz(const network_map_t *map, const char *filename);
int export_network_map_html(const network_map_t *map, const char *filename);

/* Generic export */
int export_data(const void *data, data_category_t category, const export_config_t *config);

/* Import functions */
int import_wifi_scan_json(const char *filename, wifi_scan_export_t *data);
int import_port_scan_json(const char *filename, port_scan_export_t *data);
int import_packets_pcap(const char *filename, packet_t **packets, int *count);

/* Data merging */
int export_merge_sessions(const char **session_ids, int count, const char *output_file);

/* Report generation */
typedef struct {
    session_info_t session;
    wifi_scan_export_t wifi_data;
    port_scan_export_t port_data;
    vulnerability_export_t vuln_data;
    char executive_summary[2048];
    char recommendations[2048];
} comprehensive_report_t;

int export_generate_report(const comprehensive_report_t *report, export_format_t format, const char *filename);

/* Statistics export */
typedef struct {
    int total_scans;
    int total_hosts_discovered;
    int total_vulnerabilities;
    int total_packets_captured;
    time_t first_scan;
    time_t last_scan;
    char most_common_vuln[128];
    char most_vulnerable_host[64];
} scan_statistics_t;

int export_get_statistics(const char *session_id, scan_statistics_t *stats);
int export_statistics_json(const scan_statistics_t *stats, const char *filename);

/* Utility functions */
int export_create_directory(const char *path);
int export_compress_file(const char *input, const char *output);
int export_encrypt_file(const char *input, const char *output, const char *key);
const char* export_get_default_path(data_category_t category);
char* export_generate_filename(data_category_t category, export_format_t format);

#endif /* DATA_EXPORT_H */
