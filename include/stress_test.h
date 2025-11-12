/**
 * Stress Testing Module
 * Provides network stress testing and DoS capabilities for authorized testing
 */

#ifndef STRESS_TEST_H
#define STRESS_TEST_H

#include "darknet.h"

/* Attack types */
typedef enum {
    STRESS_TCP_SYN_FLOOD,
    STRESS_TCP_ACK_FLOOD,
    STRESS_UDP_FLOOD,
    STRESS_ICMP_FLOOD,
    STRESS_HTTP_FLOOD,
    STRESS_SLOWLORIS,
    STRESS_DNS_AMPLIFICATION,
    STRESS_NTP_AMPLIFICATION,
    STRESS_SMURF,
    STRESS_FRAGMENTATION
} stress_attack_type_t;

/* Stress test configuration */
typedef struct {
    stress_attack_type_t type;
    ipv4_addr_t target_ip;
    uint16_t target_port;
    int duration_sec;
    int packets_per_sec;
    int thread_count;
    bool randomize_source;
    bool randomize_payload;
    int payload_size;
    char *payload_data;
} stress_config_t;

/* Attack statistics */
typedef struct {
    uint64_t packets_sent;
    uint64_t bytes_sent;
    uint64_t packets_failed;
    uint64_t duration_ms;
    double packets_per_second;
    double megabits_per_second;
} stress_stats_t;

/* TCP flood attacks */
int stress_tcp_syn_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_tcp_ack_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_tcp_rst_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_tcp_fin_flood(const stress_config_t *config, stress_stats_t *stats);

/* UDP flood attacks */
int stress_udp_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_udp_fragment_flood(const stress_config_t *config, stress_stats_t *stats);

/* ICMP attacks */
int stress_icmp_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_ping_of_death(const ipv4_addr_t *target);
int stress_smurf_attack(const ipv4_addr_t *target, const ipv4_addr_t *broadcast_addr);

/* Application layer attacks */
typedef struct {
    char url[512];
    char method[16];
    char user_agent[256];
    char headers[1024];
    int connections;
    int requests_per_connection;
} http_flood_config_t;

int stress_http_flood(const http_flood_config_t *config, stress_stats_t *stats);
int stress_slowloris(const ipv4_addr_t *target, uint16_t port, int connections, int duration_sec);
int stress_slow_post(const char *url, int connections, int duration_sec);

/* DNS attacks */
typedef struct {
    ipv4_addr_t target_ip;
    ipv4_addr_t *dns_servers;
    int dns_server_count;
    char *query_domains;
    int query_count;
} dns_flood_config_t;

int stress_dns_flood(const dns_flood_config_t *config, stress_stats_t *stats);
int stress_dns_amplification(const ipv4_addr_t *target, const ipv4_addr_t *dns_server, const char *domain);

/* NTP amplification */
int stress_ntp_amplification(const ipv4_addr_t *target, const ipv4_addr_t *ntp_server);

/* Fragmentation attacks */
int stress_ip_fragment_flood(const stress_config_t *config, stress_stats_t *stats);
int stress_teardrop_attack(const ipv4_addr_t *target);

/* Mixed attacks */
int stress_mixed_flood(const stress_config_t *configs, int config_count, stress_stats_t *stats);

/* Bandwidth testing */
typedef struct {
    ipv4_addr_t target_ip;
    uint16_t target_port;
    int duration_sec;
    int target_bandwidth_mbps;
    bool tcp;
} bandwidth_test_config_t;

int stress_bandwidth_test(const bandwidth_test_config_t *config, stress_stats_t *stats);

/* Connection exhaustion */
int stress_connection_flood(const ipv4_addr_t *target, uint16_t port, int max_connections, int duration_sec);
int stress_sockstress(const ipv4_addr_t *target, uint16_t port, int duration_sec);

/* Attack control */
int stress_start_attack(const stress_config_t *config);
int stress_stop_attack(void);
int stress_pause_attack(void);
int stress_resume_attack(void);
int stress_get_stats(stress_stats_t *stats);

/* Payload generation */
int stress_generate_random_payload(uint8_t *buffer, size_t size);
int stress_generate_pattern_payload(uint8_t *buffer, size_t size, const uint8_t *pattern, size_t pattern_len);

/* Rate limiting */
typedef struct {
    int packets_per_second;
    int bytes_per_second;
    int burst_size;
} rate_limit_t;

int stress_set_rate_limit(const rate_limit_t *limit);
int stress_get_rate_limit(rate_limit_t *limit);

/* Helper functions */
const char* stress_attack_type_to_string(stress_attack_type_t type);
void stress_print_stats(const stress_stats_t *stats);

#endif /* STRESS_TEST_H */
