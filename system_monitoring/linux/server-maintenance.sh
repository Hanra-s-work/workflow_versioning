#!/bin/bash

# Server Maintenance Monitoring Script
# Sends health reports and alerts via ntfy
# Designed for Ubuntu Server with limited resources

# ================================================================================
# CONFIGURATION AND CONSTANTS
# ================================================================================

# Configuration
NTFY_TOPIC="${NTFY_TOPIC:-your-server-health}"  # Set your ntfy topic
NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"  # Default ntfy server
HOSTNAME="${SERVER_NAME:-$(hostname)}"  # Allow custom server name for privacy
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"

# Thresholds (adjust as needed)
DISK_USAGE_WARNING=80
DISK_USAGE_CRITICAL=95
MEMORY_WARNING=85
MEMORY_CRITICAL=95
# Load thresholds (multiplied by 100 for integer comparison)
LOAD_WARNING=200
LOAD_CRITICAL=400
# Temperature thresholds (°C)
TEMP_WARNING=70
TEMP_CRITICAL=85
# Additional thresholds
SWAP_WARNING=50  # % of swap used
LOG_SIZE_WARNING=100  # MB for log files
PROCESS_WARNING=500  # Max processes

# Colors for console output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

# Logging function with dated files and levels
log() {
    local level="${1:-INFO}"
    local message="$2"
    local logfile="${LOG_DIR}/$(date +%Y-%m-%d).log"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] - $message" | tee -a "$logfile"
}

# Send ntfy notification with fallback
send_notification() {
    local title="$1"
    local message="$2"
    local priority="${3:-default}"  # default, low, high, urgent
    local tags="${4:-computer}"

    # Check for dry run mode
    if [ "${DRY_RUN:-false}" = "true" ]; then
        log "INFO" "DRY RUN: Would send notification - Title: $title, Priority: $priority"
        return 0
    fi

    if ! command -v curl >/dev/null 2>&1; then
        log "WARNING" "curl not available, skipping ntfy notification"
        return 1
    fi

    local ntfy_url="$NTFY_SERVER/$NTFY_TOPIC"
    local fallback_url="https://ntfy.sh/$NTFY_TOPIC"

    # Try custom ntfy server first
    log "INFO" "Attempting to send notification to custom server: $NTFY_SERVER"
    if curl -s --max-time 10 \
            -H "Title: $title" \
            -H "Priority: $priority" \
            -H "Tags: $tags" \
            -d "$message" \
            "$ntfy_url" >/dev/null 2>&1; then
        log "INFO" "[OK] Notification sent successfully to custom server"
        return 0
    else
        log "WARNING" "[WARNING] Custom ntfy server failed, trying fallback server: ntfy.sh"
        # Try fallback ntfy.sh server
        if curl -s --max-time 10 \
                -H "Title: $title" \
                -H "Priority: $priority" \
                -H "Tags: $tags" \
                -d "$message" \
                "$fallback_url" >/dev/null 2>&1; then
            log "INFO" "[OK] Notification sent successfully to fallback server (ntfy.sh)"
            return 0
        else
            log "ERROR" "[ERROR] Both custom and fallback ntfy servers failed"
            return 1
        fi
    fi
}

# ================================================================================
# DISK MONITORING FUNCTIONS
# ================================================================================

# Check disk usage
check_disk_usage() {
    log "INFO" "Checking disk usage..."

    local alerts=""
    local warnings=""

    # Check all mounted filesystems
    while IFS= read -r line; do
        # Skip header line and tmpfs/squashfs
        [[ "$line" =~ ^Filesystem ]] && continue
        [[ "$line" =~ tmpfs|squashfs ]] && continue

        local filesystem=$(echo "$line" | awk '{print $1}')
        local usage_percent=$(echo "$line" | awk '{print $5}' | sed 's/%//')

        if [ "$usage_percent" -ge "$DISK_USAGE_CRITICAL" ]; then
            alerts="${alerts}[CRITICAL] $filesystem is ${usage_percent}% full\n"
        elif [ "$usage_percent" -ge "$DISK_USAGE_WARNING" ]; then
            warnings="${warnings}[WARNING] $filesystem is ${usage_percent}% full\n"
        fi
    done < <(df -h)

    echo "$alerts$warnings"
}

# Check disk health (SMART)
check_disk_health() {
    log "INFO" "Checking disk health (SMART)..."

    local alerts=""
    local warnings=""

    # Check if smartctl is available
    if ! command -v smartctl >/dev/null 2>&1; then
        log "WARNING" "smartctl not available, skipping SMART checks"
        return ""
    fi

    # Find disk devices
    for disk in /dev/sd[a-z] /dev/nvme[0-9]; do
        if [ -b "$disk" ]; then
            log "INFO" "Checking SMART status for $disk"

            # Get SMART health status
            if smart_status=$(smartctl -H "$disk" 2>/dev/null); then
                if echo "$smart_status" | grep -q "PASSED"; then
                    log "INFO" "SMART: $disk PASSED"
                elif echo "$smart_status" | grep -q "FAILED"; then
                    alerts="${alerts}[CRITICAL] SMART check FAILED for $disk\n"
                else
                    warnings="${warnings}[WARNING] SMART status unknown for $disk\n"
                fi
            fi

            # Check for reallocated sectors (mechanical drives)
            if smartctl -A "$disk" 2>/dev/null | grep -q "Reallocated_Sector_Ct"; then
                reallocated=$(smartctl -A "$disk" 2>/dev/null | grep "Reallocated_Sector_Ct" | awk '{print $10}')
                if [ "$reallocated" -gt 0 ]; then
                    warnings="${warnings}[WARNING] $disk has $reallocated reallocated sectors\n"
                fi
            fi
        fi
    done

    echo "$alerts$warnings"
}

# ================================================================================
# SYSTEM RESOURCE MONITORING FUNCTIONS
# ================================================================================

# Check system resources
check_system_resources() {
    log "INFO" "Checking system resources..."

    local alerts=""
    local warnings=""

    # Check memory usage
    alerts="${alerts}$(check_memory_usage)"
    warnings="${warnings}$(check_load_average)"

    echo "$alerts$warnings"
}

# Check memory usage specifically
check_memory_usage() {
    local mem_info=$(free | grep "^Mem:")
    local mem_total=$(echo "$mem_info" | awk '{print $2}')
    local mem_used=$(echo "$mem_info" | awk '{print $3}')
    local mem_percent=$((mem_used * 100 / mem_total))

    if [ "$mem_percent" -ge "$MEMORY_CRITICAL" ]; then
        echo "[CRITICAL] Memory usage is ${mem_percent}%\n"
    elif [ "$mem_percent" -ge "$MEMORY_WARNING" ]; then
        echo "[WARNING] Memory usage is ${mem_percent}%\n"
    fi
}

# Check load average specifically
check_load_average() {
    # Load average (1 minute) - handle both US (.) and European (,) decimal formats
    local load_avg_raw=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,$//')
    # Convert European comma to US dot for calculation
    local load_avg=$(echo "$load_avg_raw" | sed 's/,/\./')
    local load_num=$(echo "$load_avg" | awk '{print int($1 * 100)}')

    if [ "$load_num" -ge "$LOAD_CRITICAL" ]; then
        echo "[CRITICAL] Load average is $load_avg_raw\n"
    elif [ "$load_num" -ge "$LOAD_WARNING" ]; then
        echo "[WARNING] Load average is $load_avg_raw\n"
    fi
}

# Check system temperatures
check_temperatures() {
    log "INFO" "Checking system temperatures..."

    local alerts=""
    local warnings=""

    # Check if sensors command is available
    if ! command -v sensors >/dev/null 2>&1; then
        log "WARNING" "sensors command not available, skipping temperature checks"
        echo "[WARNING] Temperature monitoring unavailable (install lm-sensors)\n"
        return
    fi

    # Get temperature readings
    local temp_output=$(sensors 2>/dev/null)
    local max_temp=0

    # Parse temperature readings (look for lines with °C)
    while IFS= read -r line; do
        if echo "$line" | grep -q "°C"; then
            # Extract temperature value (handle both +XX.X°C and XX.X°C formats)
            local temp_value=$(echo "$line" | grep -o "[0-9]\+\.[0-9]\+" | head -1)
            if [ -n "$temp_value" ]; then
                # Convert to integer for comparison
                local temp_int=$(echo "$temp_value" | awk '{print int($1)}')
                if [ "$temp_int" -gt "$max_temp" ]; then
                    max_temp=$temp_int
                fi
            fi
        fi
    done <<< "$temp_output"

    if [ "$max_temp" -ge "$TEMP_CRITICAL" ]; then
        alerts="${alerts}[CRITICAL] System temperature is ${max_temp}°C\n"
    elif [ "$max_temp" -ge "$TEMP_WARNING" ]; then
        warnings="${warnings}[WARNING] System temperature is ${max_temp}°C\n"
    fi

    echo "$alerts$warnings"
}

# Check swap usage
check_swap_usage() {
    log "INFO" "Checking swap usage..."

    local alerts=""
    local warnings=""

    # Check if swap exists
    if ! grep -q "partition\|file" /proc/swaps 2>/dev/null; then
        log "INFO" "No swap configured on this system"
        echo "[INFO] No swap space configured\n"
        return
    fi

    local swap_info=$(free | grep "^Swap:")
    local swap_total=$(echo "$swap_info" | awk '{print $2}')
    local swap_used=$(echo "$swap_info" | awk '{print $3}')

    if [ "$swap_total" -gt 0 ]; then
        local swap_percent=$((swap_used * 100 / swap_total))

        if [ "$swap_percent" -ge "$SWAP_WARNING" ]; then
            warnings="${warnings}[WARNING] Swap usage is ${swap_percent}% (${swap_used}KB/${swap_total}KB)\n"
        fi
    fi

    echo "$alerts$warnings"
}

# Check log file sizes
check_log_sizes() {
    log "INFO" "Checking log file sizes..."

    local alerts=""
    local warnings=""

    # Common log files to check
    local log_files=("/var/log/syslog" "/var/log/auth.log" "/var/log/kern.log" "/var/log/dmesg")

    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            local size_mb=$(du -m "$log_file" 2>/dev/null | awk '{print $1}')
            if [ "$size_mb" -ge "$LOG_SIZE_WARNING" ]; then
                warnings="${warnings}[WARNING] Log file $log_file is ${size_mb}MB\n"
            fi
        fi
    done

    echo "$alerts$warnings"
}

# Check process information
check_processes() {
    log "INFO" "Checking process information..."

    local alerts=""
    local warnings=""

    # Total process count
    local total_processes=$(ps aux --no-headers | wc -l)
    if [ "$total_processes" -ge "$PROCESS_WARNING" ]; then
        warnings="${warnings}[WARNING] High process count: $total_processes\n"
    fi

    # Zombie processes
    local zombie_count=$(ps aux | awk '{print $8}' | grep -c "Z")
    if [ "$zombie_count" -gt 0 ]; then
        alerts="${alerts}[CRITICAL] $zombie_count zombie processes detected\n"
    fi

    echo "$alerts$warnings"
}

# ================================================================================
# NETWORK MONITORING FUNCTIONS
# ================================================================================

# Check network I/O and connections
check_network() {
    log "INFO" "Checking network status..."

    local alerts=""
    local warnings=""

    # Check for network errors (if available)
    if command -v ip >/dev/null 2>&1; then
        local errors=$(ip -s link | grep -A1 "RX errors" | tail -1 | awk '{print $3}' | sed 's/[^0-9]//g')
        if [ "${errors:-0}" -gt 0 ]; then
            warnings="${warnings}[WARNING] Network RX errors detected: $errors\n"
        fi
    fi

    # Check established connections (basic)
    local established=$(ss -t state established 2>/dev/null | wc -l || netstat -t 2>/dev/null | grep ESTABLISHED | wc -l || echo "0")
    if [ "$established" -gt 1000 ]; then
        warnings="${warnings}[WARNING] High number of established connections: $established\n"
    fi

    echo "$alerts$warnings"
}

# ================================================================================
# KUBERNETES MONITORING FUNCTIONS
# ================================================================================

# Check Kubernetes cluster status (optional)
check_kubernetes() {
    log "INFO" "Checking Kubernetes cluster status..."

    local alerts=""
    local warnings=""

    # Check kubectl availability and functionality
    if ! check_kubectl_available; then
        return
    fi

    # Check cluster connectivity
    if ! check_kubernetes_connectivity; then
        return
    fi

    # Check node health
    alerts="${alerts}$(check_kubernetes_nodes)"

    # Check pod health
    warnings="${warnings}$(check_kubernetes_pods)"

    # Check recent events
    warnings="${warnings}$(check_kubernetes_events)"

    # Optional resource check
    if [ "${K8S_RESOURCE_CHECK:-false}" = "true" ]; then
        warnings="${warnings}$(check_kubernetes_resources)"
    fi

    echo "$alerts$warnings"
}

# Check if kubectl is available and functional
check_kubectl_available() {
    # Check if kubectl command exists
    if ! command -v kubectl >/dev/null 2>&1; then
        log "kubectl not available, skipping Kubernetes checks"
        return 1
    fi

    # Test if kubectl can execute basic commands (handles wrapper scripts)
    if ! kubectl version --client --short >/dev/null 2>&1; then
        log "kubectl available but not functional (may need sudo or special setup)"
        echo "[WARNING] kubectl available but not functional (check permissions/setup)\n"
        return 1
    fi

    return 0
}

# Check Kubernetes cluster connectivity
check_kubernetes_connectivity() {
    # Test cluster connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        echo "[WARNING] Cannot connect to Kubernetes cluster (check kubeconfig/permissions)\n"
        return 1
    fi
    return 0
}

# Check Kubernetes node health
check_kubernetes_nodes() {
    local unhealthy_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -v " Ready" | wc -l)
    if [ "$unhealthy_nodes" -gt 0 ]; then
        echo "[CRITICAL] $unhealthy_nodes Kubernetes nodes are not ready\n"
    fi
}

# Check Kubernetes pod health
check_kubernetes_pods() {
    local total_pods=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l)
    local unhealthy_pods=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | grep -E "Error|CrashLoopBackOff|Pending" | wc -l)

    if [ "$unhealthy_pods" -gt 0 ]; then
        echo "[WARNING] $unhealthy_pods pods in unhealthy state\n"
    fi
}

# Check recent Kubernetes events
check_kubernetes_events() {
    local recent_events=$(kubectl get events --all-namespaces --field-selector type=Warning --no-headers 2>/dev/null | awk '$1 > "'$(date -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -v-5M +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo "1970-01-01T00:00:00")'"' | wc -l)

    if [ "$recent_events" -gt 0 ]; then
        echo "[WARNING] $recent_events warning events in last 5 minutes\n"
    fi
}

# Check Kubernetes resource usage
check_kubernetes_resources() {
    local high_cpu_pods=$(kubectl top pods --all-namespaces --no-headers 2>/dev/null | awk '$3 > 80 {count++} END {print count+0}')
    if [ "$high_cpu_pods" -gt 0 ]; then
        echo "[WARNING] $high_cpu_pods pods using >80% CPU\n"
    fi
}

# ================================================================================
# SERVICE MONITORING FUNCTIONS
# ================================================================================

# Check system services
check_services() {
    log "INFO" "Checking critical services..."

    local alerts=""
    local warnings=""

    # Check if services are running (add your critical services here)
    local critical_services=("cron" "systemd-journald")

    # Only check sshd if it's installed (for server environments)
    if systemctl list-units --all | grep -q "sshd.service"; then
        critical_services+=("sshd")
    fi

    for service in "${critical_services[@]}"; do
        if ! systemctl is-active --quiet "$service" 2>/dev/null; then
            alerts="${alerts}[CRITICAL] Service $service is not running\n"
        fi
    done

    echo "$alerts$warnings"
}

# ================================================================================
# MAIN EXECUTION
# ================================================================================

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                echo "Server Maintenance Monitoring Script"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --help, -h          Show this help message"
                echo "  --version, -v       Show version information"
                echo "  --dry-run           Run checks but don't send notifications"
                echo ""
                echo "Environment Variables:"
                echo "  NTFY_TOPIC          Your ntfy topic (default: server-health)"
                echo "  NTFY_SERVER         Your ntfy server URL (default: https://ntfy.sh)"
                echo "  SERVER_NAME         Custom name for the server (default: hostname, for privacy)"
                echo "  SEND_NORMAL_STATUS  Send notifications even when healthy (default: false)"
                echo "  K8S_RESOURCE_CHECK  Enable detailed K8s resource monitoring (default: false)"
                echo ""
                echo "This script monitors comprehensive server health including disk usage, SMART status,"
                echo "system resources, temperatures, swap usage, log files, processes, network I/O,"
                echo "Kubernetes cluster status (if available), and critical services. Results are sent via ntfy."
                exit 0
                ;;
            --version|-v)
                echo "Server Maintenance Script v1.0"
                exit 0
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    log "=== Starting server maintenance check ==="

    # Run all checks
    local disk_alerts=$(check_disk_usage)
    local health_alerts=$(check_disk_health)
    local resource_alerts=$(check_system_resources)
    local temp_alerts=$(check_temperatures)
    local swap_alerts=$(check_swap_usage)
    local log_alerts=$(check_log_sizes)
    local process_alerts=$(check_processes)
    local network_alerts=$(check_network)
    local k8s_alerts=$(check_kubernetes)
    local service_alerts=$(check_services)

    # Combine all alerts
    local all_alerts="$disk_alerts$health_alerts$resource_alerts$temp_alerts$swap_alerts$log_alerts$process_alerts$network_alerts$k8s_alerts$service_alerts"
    local critical_alerts=$(echo "$all_alerts" | grep "\[CRITICAL\]" || true)
    local warning_alerts=$(echo "$all_alerts" | grep "\[WARNING\]" || true)

    # Determine notification priority and content
    if [ -n "$critical_alerts" ]; then
        # Critical issues - urgent priority
        local title="🚨 $HOSTNAME - Critical Issues Detected"
        local message="Critical system issues require immediate attention:

$critical_alerts
$(date '+%Y-%m-%d %H:%M:%S')"
        send_notification "$title" "$message" "urgent" "warning"

        # Also log warnings if any
        if [ -n "$warning_alerts" ]; then
            message="$message

Warnings:
$warning_alerts"
        fi

        echo -e "${RED}CRITICAL ISSUES DETECTED:${NC}"
        echo "$critical_alerts"

    elif [ -n "$warning_alerts" ]; then
        # Warnings only - high priority
        local title="⚠️ $HOSTNAME - System Warnings"
        local message="System warnings detected:

$warning_alerts
$(date '+%Y-%m-%d %H:%M:%S')"
        send_notification "$title" "$message" "high" "warning"

        echo -e "${YELLOW}WARNINGS DETECTED:${NC}"
        echo "$warning_alerts"

    else
        # All good - normal status (low priority, only if configured)
        if [ "${SEND_NORMAL_STATUS:-false}" = "true" ]; then
            local title="✅ $HOSTNAME - System Healthy"
            local message="All systems operational - $(date '+%Y-%m-%d %H:%M:%S')"
            send_notification "$title" "$message" "low" "white_check_mark"
        fi

        echo -e "${GREEN}All systems operational${NC}"
    fi

    log "=== Maintenance check completed ==="
}

# Run main function
main "$@"
