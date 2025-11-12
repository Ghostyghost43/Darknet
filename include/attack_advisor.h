/**
 * Attack Advisor Module
 * AI-powered attack recommendation based on discovered vulnerabilities
 */

#ifndef ATTACK_ADVISOR_H
#define ATTACK_ADVISOR_H

#include "darknet.h"
#include "network_scan.h"
#include "wifi_attacks.h"

/* Attack types */
typedef enum {
    ATTACK_TYPE_WIFI_DEAUTH,
    ATTACK_TYPE_WIFI_EVIL_TWIN,
    ATTACK_TYPE_WIFI_WPS,
    ATTACK_TYPE_BRUTE_FORCE_SSH,
    ATTACK_TYPE_BRUTE_FORCE_FTP,
    ATTACK_TYPE_BRUTE_FORCE_SMB,
    ATTACK_TYPE_BRUTE_FORCE_RDP,
    ATTACK_TYPE_SQL_INJECTION,
    ATTACK_TYPE_XSS,
    ATTACK_TYPE_ARP_POISON,
    ATTACK_TYPE_MITM,
    ATTACK_TYPE_DOS_SYN_FLOOD,
    ATTACK_TYPE_DOS_UDP_FLOOD,
    ATTACK_TYPE_EXPLOIT_CVE,
    ATTACK_TYPE_PASSWORD_SPRAY,
    ATTACK_TYPE_PHISHING
} attack_type_t;

/* Attack difficulty */
typedef enum {
    DIFFICULTY_TRIVIAL,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    DIFFICULTY_EXPERT
} attack_difficulty_t;

/* Success probability */
typedef enum {
    PROBABILITY_VERY_LOW,    /* < 20% */
    PROBABILITY_LOW,         /* 20-40% */
    PROBABILITY_MEDIUM,      /* 40-60% */
    PROBABILITY_HIGH,        /* 60-80% */
    PROBABILITY_VERY_HIGH    /* > 80% */
} success_probability_t;

/* Attack recommendation */
typedef struct {
    attack_type_t type;
    char name[128];
    char description[512];
    attack_difficulty_t difficulty;
    success_probability_t probability;
    int priority;  /* 1-10, 10 being highest */
    char target[256];
    char prerequisites[512];
    char command_example[512];
    char expected_result[256];
    int estimated_time_minutes;
    bool requires_custom_wordlist;
    bool noisy;  /* Will it be detected easily? */
    float risk_score;  /* 0.0-10.0 */
} attack_recommendation_t;

/* Analysis context */
typedef struct {
    host_info_t *hosts;
    int host_count;
    wifi_ap_t *access_points;
    int ap_count;
    vulnerability_t *vulnerabilities;
    int vuln_count;
    port_scan_result_t *open_ports;
    int port_count;
} network_analysis_t;

/* Advisor configuration */
typedef struct {
    bool include_high_risk;
    bool include_noisy_attacks;
    bool prefer_automated;
    int max_recommendations;
    attack_difficulty_t max_difficulty;
    bool only_high_probability;
} advisor_config_t;

/* Get attack recommendations */
int advisor_analyze_network(const network_analysis_t *analysis, const advisor_config_t *config,
                            attack_recommendation_t **recommendations, int *count);

/* Specific analyzers */
int advisor_analyze_wifi(const wifi_ap_t *aps, int ap_count, attack_recommendation_t **recommendations, int *count);
int advisor_analyze_host(const host_info_t *host, const port_scan_result_t *ports, int port_count,
                         attack_recommendation_t **recommendations, int *count);
int advisor_analyze_vulnerability(const vulnerability_t *vuln, attack_recommendation_t **recommendations, int *count);

/* Attack planning */
typedef struct {
    attack_recommendation_t *attacks;
    int attack_count;
    char attack_chain[2048];  /* Description of attack sequence */
    int total_estimated_time;
    float overall_success_probability;
    char critical_path[1024];
} attack_plan_t;

int advisor_create_attack_plan(const attack_recommendation_t *recommendations, int count,
                               attack_plan_t *plan);
int advisor_optimize_attack_chain(attack_plan_t *plan);

/* Real-time suggestions */
typedef void (*attack_suggestion_callback_t)(const attack_recommendation_t *recommendation, void *user_data);

int advisor_monitor_and_suggest(const char *interface, attack_suggestion_callback_t callback, void *user_data);

/* Attack effectiveness scoring */
float advisor_calculate_effectiveness(attack_type_t type, const network_analysis_t *analysis);
float advisor_calculate_stealth_score(attack_type_t type);
float advisor_calculate_impact_score(attack_type_t type, const char *target);

/* Wordlist recommendations */
int advisor_suggest_wordlist(attack_type_t type, const char *target, char *wordlist_path, size_t len);
int advisor_generate_custom_wordlist(const host_info_t *host, const char *output_file);

/* Defense detection */
typedef struct {
    bool ids_detected;
    bool ips_detected;
    bool firewall_detected;
    bool rate_limiting_detected;
    bool honey_pot_suspected;
    char defense_details[512];
} defense_analysis_t;

int advisor_analyze_defenses(const char *target, defense_analysis_t *defenses);
int advisor_suggest_evasion(const defense_analysis_t *defenses, char *evasion_strategy, size_t len);

/* Attack templates */
typedef struct {
    attack_type_t type;
    char template_command[512];
    char *parameters[16];
    int parameter_count;
    char description[256];
} attack_template_t;

int advisor_get_attack_template(attack_type_t type, attack_template_t *template);
int advisor_generate_command(const attack_recommendation_t *recommendation, char *command, size_t len);

/* Historical analysis */
typedef struct {
    attack_type_t type;
    int attempts;
    int successes;
    float success_rate;
    int avg_time_minutes;
} attack_history_t;

int advisor_load_attack_history(attack_history_t **history, int *count);
int advisor_update_attack_history(attack_type_t type, bool success, int time_minutes);
int advisor_learn_from_history(attack_recommendation_t *recommendation);

/* Reporting */
int advisor_export_recommendations(const attack_recommendation_t *recommendations, int count,
                                   const char *filename);
int advisor_generate_attack_report(const attack_plan_t *plan, const char *filename);

/* Utility functions */
const char* advisor_attack_type_to_string(attack_type_t type);
const char* advisor_difficulty_to_string(attack_difficulty_t difficulty);
const char* advisor_probability_to_string(success_probability_t probability);
void advisor_print_recommendation(const attack_recommendation_t *recommendation);
void advisor_print_attack_plan(const attack_plan_t *plan);

#endif /* ATTACK_ADVISOR_H */
