#!/bin/bash

# Dragon KARAU AI - Log Monitoring Dashboard
# Real-time monitoring of all critical logs

# Colors for output
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m' # No Color

# Log file paths
HEALTH_LOG="/var/log/dragon-karau-health.log"
VALIDATION_LOG="/var/log/dragon-karau-validation.log"
EXPO_LOG="/var/log/supervisor/expo.out.log"
BACKEND_LOG="/var/log/supervisor/backend.out.log"

clear

echo -e "${COLOR_CYAN}╔════════════════════════════════════════════════════════════════╗${COLOR_NC}"
echo -e "${COLOR_CYAN}║         Dragon KARAU AI - Log Monitoring Dashboard            ║${COLOR_NC}"
echo -e "${COLOR_CYAN}╚════════════════════════════════════════════════════════════════╝${COLOR_NC}"
echo ""

# Function to count log entries
count_log_entries() {
    LOG_FILE=$1
    if [ -f "$LOG_FILE" ]; then
        wc -l < "$LOG_FILE"
    else
        echo "0"
    fi
}

# Function to get recent errors
get_recent_errors() {
    LOG_FILE=$1
    PATTERN=$2
    if [ -f "$LOG_FILE" ]; then
        grep -i "$PATTERN" "$LOG_FILE" 2>/dev/null | tail -5
    fi
}

# Function to show service status
show_service_status() {
    echo -e "${COLOR_BLUE}═══ Service Status ═══${COLOR_NC}"
    echo ""
    
    supervisorctl status | while read line; do
        SERVICE=$(echo "$line" | awk '{print $1}')
        STATUS=$(echo "$line" | awk '{print $2}')
        
        if [ "$STATUS" = "RUNNING" ]; then
            echo -e "  ${COLOR_GREEN}✓${COLOR_NC} $SERVICE: $STATUS"
        else
            echo -e "  ${COLOR_RED}✗${COLOR_NC} $SERVICE: $STATUS"
        fi
    done
    echo ""
}

# Function to show health check summary
show_health_summary() {
    echo -e "${COLOR_BLUE}═══ Health Check Summary (Last 24h) ═══${COLOR_NC}"
    echo ""
    
    if [ -f "$HEALTH_LOG" ]; then
        TOTAL_CHECKS=$(grep -c "Starting health check cycle" "$HEALTH_LOG" 2>/dev/null || echo "0")
        SUCCESS_CHECKS=$(grep -c "Health check cycle complete" "$HEALTH_LOG" 2>/dev/null || echo "0")
        RESTARTS=$(grep -c "Attempting to restart" "$HEALTH_LOG" 2>/dev/null || echo "0")
        ALERTS=$(grep -c "ALERT" "$HEALTH_LOG" 2>/dev/null || echo "0")
        
        echo -e "  Total Health Checks: ${COLOR_CYAN}$TOTAL_CHECKS${COLOR_NC}"
        echo -e "  Successful Checks: ${COLOR_GREEN}$SUCCESS_CHECKS${COLOR_NC}"
        echo -e "  Service Restarts: ${COLOR_YELLOW}$RESTARTS${COLOR_NC}"
        echo -e "  Critical Alerts: ${COLOR_RED}$ALERTS${COLOR_NC}"
        
        if [ "$ALERTS" -gt 0 ]; then
            echo ""
            echo -e "  ${COLOR_RED}Recent Alerts:${COLOR_NC}"
            grep "ALERT" "$HEALTH_LOG" | tail -3 | while read line; do
                echo -e "    ${COLOR_RED}⚠${COLOR_NC} $line"
            done
        fi
    else
        echo -e "  ${COLOR_YELLOW}No health log file found${COLOR_NC}"
    fi
    echo ""
}

# Function to show configuration validation summary
show_validation_summary() {
    echo -e "${COLOR_BLUE}═══ Configuration Validation ═══${COLOR_NC}"
    echo ""
    
    if [ -f "$VALIDATION_LOG" ]; then
        LAST_VALIDATION=$(tail -20 "$VALIDATION_LOG" 2>/dev/null)
        
        if echo "$LAST_VALIDATION" | grep -q "All critical checks passed"; then
            echo -e "  ${COLOR_GREEN}✓ Last validation: PASSED${COLOR_NC}"
        elif echo "$LAST_VALIDATION" | grep -q "check(s) failed"; then
            FAILED=$(echo "$LAST_VALIDATION" | grep "check(s) failed" | grep -oE "[0-9]+ check")
            echo -e "  ${COLOR_RED}✗ Last validation: $FAILED FAILED${COLOR_NC}"
        else
            echo -e "  ${COLOR_YELLOW}⚠ Validation status unknown${COLOR_NC}"
        fi
        
        LAST_RUN=$(stat -c %y "$VALIDATION_LOG" 2>/dev/null | cut -d'.' -f1)
        echo -e "  Last run: ${COLOR_CYAN}$LAST_RUN${COLOR_NC}"
    else
        echo -e "  ${COLOR_YELLOW}No validation log file found${COLOR_NC}"
    fi
    echo ""
}

# Function to show recent errors
show_recent_errors() {
    echo -e "${COLOR_BLUE}═══ Recent Errors (Last 10) ═══${COLOR_NC}"
    echo ""
    
    # Frontend errors
    if [ -f "$EXPO_LOG" ]; then
        EXPO_ERRORS=$(grep -i "error\|exception\|failed" "$EXPO_LOG" 2>/dev/null | tail -5)
        if [ -n "$EXPO_ERRORS" ]; then
            echo -e "${COLOR_YELLOW}Frontend (Expo):${COLOR_NC}"
            echo "$EXPO_ERRORS" | while read line; do
                echo -e "  ${COLOR_RED}⚠${COLOR_NC} $(echo "$line" | cut -c1-100)"
            done
            echo ""
        fi
    fi
    
    # Backend errors
    if [ -f "$BACKEND_LOG" ]; then
        BACKEND_ERRORS=$(grep -i "error\|exception\|failed" "$BACKEND_LOG" 2>/dev/null | tail -5)
        if [ -n "$BACKEND_ERRORS" ]; then
            echo -e "${COLOR_YELLOW}Backend:${COLOR_NC}"
            echo "$BACKEND_ERRORS" | while read line; do
                echo -e "  ${COLOR_RED}⚠${COLOR_NC} $(echo "$line" | cut -c1-100)"
            done
            echo ""
        fi
    fi
    
    if [ -z "$EXPO_ERRORS" ] && [ -z "$BACKEND_ERRORS" ]; then
        echo -e "  ${COLOR_GREEN}✓ No recent errors found${COLOR_NC}"
        echo ""
    fi
}

# Function to show disk usage
show_disk_usage() {
    echo -e "${COLOR_BLUE}═══ Disk Usage ═══${COLOR_NC}"
    echo ""
    
    DISK_USAGE=$(df -h / | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -gt 80 ]; then
        echo -e "  ${COLOR_RED}⚠ Disk usage: ${DISK_USAGE}% (HIGH)${COLOR_NC}"
    elif [ "$DISK_USAGE" -gt 60 ]; then
        echo -e "  ${COLOR_YELLOW}⚠ Disk usage: ${DISK_USAGE}% (MODERATE)${COLOR_NC}"
    else
        echo -e "  ${COLOR_GREEN}✓ Disk usage: ${DISK_USAGE}% (NORMAL)${COLOR_NC}"
    fi
    
    echo ""
}

# Function to show memory usage
show_memory_usage() {
    echo -e "${COLOR_BLUE}═══ Memory Usage ═══${COLOR_NC}"
    echo ""
    
    free -h | grep Mem | awk '{print "  Total: "$2" | Used: "$3" | Free: "$4}'
    
    echo ""
}

# Main monitoring display
show_service_status
show_health_summary
show_validation_summary
show_recent_errors
show_disk_usage
show_memory_usage

echo -e "${COLOR_CYAN}═══ Log Files ═══${COLOR_NC}"
echo ""
echo "  Health Check:       $HEALTH_LOG"
echo "  Config Validation:  $VALIDATION_LOG"
echo "  Frontend (Expo):    $EXPO_LOG"
echo "  Backend:            $BACKEND_LOG"
echo ""

echo -e "${COLOR_CYAN}═══ Quick Commands ═══${COLOR_NC}"
echo ""
echo "  View health log:        tail -f $HEALTH_LOG"
echo "  View validation log:    tail -f $VALIDATION_LOG"
echo "  View frontend log:      sudo supervisorctl tail -f expo"
echo "  View backend log:       sudo supervisorctl tail -f backend"
echo "  Run health check:       /app/scripts/health_check.sh"
echo "  Validate config:        /app/scripts/validate_config.sh"
echo ""

echo -e "${COLOR_GREEN}Press Ctrl+C to exit, or add '-f' flag for continuous monitoring${COLOR_NC}"

# If -f flag is provided, continuously monitor
if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
    echo ""
    echo "Monitoring logs in real-time (updating every 10 seconds)..."
    echo ""
    
    while true; do
        sleep 10
        clear
        $0  # Re-run this script
    done
fi
