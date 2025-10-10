#!/bin/bash
"""
Kagema FM Emergent Tunnel Watchdog
Modern tunnel monitoring for Emergent platform infrastructure
Replaces legacy ngrok-based monitoring with proper Emergent tunnel validation
"""

LOG_FILE="/var/log/emergent_tunnel_watchdog.log"

# Configuration for Emergent tunnels
EMERGENT_TUNNEL_URL="https://carmedia-hub-1.preview.emergentagent.com"
BACKEND_HEALTH_ENDPOINT="/api/"
FRONTEND_HEALTH_ENDPOINT="/"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_emergent_tunnel_health() {
    local url="$1"
    local endpoint="$2"
    local full_url="${url}${endpoint}"
    
    # Test tunnel connectivity with proper timeout and error handling
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}|TIME:%{time_total}" \
                         --max-time 10 \
                         --connect-timeout 5 \
                         "$full_url" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
        local time=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
        
        if [[ "$status" =~ ^[2-3][0-9][0-9]$ ]]; then
            echo "SUCCESS|$status|$time"
            return 0
        else
            echo "HTTP_ERROR|$status|$time"
            return 1
        fi
    else
        echo "CONNECTION_ERROR|0|0"
        return 1
    fi
}

validate_tunnel_system() {
    log_message "🔍 Validating Emergent tunnel system..."
    
    # Check backend health
    local backend_result=$(check_emergent_tunnel_health "$EMERGENT_TUNNEL_URL" "$BACKEND_HEALTH_ENDPOINT")
    local backend_status=$(echo "$backend_result" | cut -d'|' -f1)
    local backend_code=$(echo "$backend_result" | cut -d'|' -f2)
    local backend_time=$(echo "$backend_result" | cut -d'|' -f3)
    
    # Check frontend health  
    local frontend_result=$(check_emergent_tunnel_health "$EMERGENT_TUNNEL_URL" "$FRONTEND_HEALTH_ENDPOINT")
    local frontend_status=$(echo "$frontend_result" | cut -d'|' -f1)
    local frontend_code=$(echo "$frontend_result" | cut -d'|' -f2)
    local frontend_time=$(echo "$frontend_result" | cut -d'|' -f3)
    
    # Log results
    if [[ "$backend_status" == "SUCCESS" ]]; then
        log_message "✅ Backend tunnel healthy: HTTP $backend_code (${backend_time}s)"
    else
        log_message "❌ Backend tunnel issue: $backend_status HTTP $backend_code"
    fi
    
    if [[ "$frontend_status" == "SUCCESS" ]]; then
        log_message "✅ Frontend tunnel healthy: HTTP $frontend_code (${frontend_time}s)"
    else
        log_message "❌ Frontend tunnel issue: $frontend_status HTTP $frontend_code"
    fi
    
    # Return overall status
    if [[ "$backend_status" == "SUCCESS" && "$frontend_status" == "SUCCESS" ]]; then
        return 0
    else
        return 1
    fi
}

handle_tunnel_degradation() {
    local issue_type="$1"
    log_message "⚠️ Tunnel degradation detected: $issue_type"
    
    # Intelligent recovery based on issue type
    case "$issue_type" in
        "CONNECTION_ERROR")
            log_message "🔄 Connection issue detected - checking network connectivity"
            # Test basic network connectivity
            if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
                log_message "✅ Network connectivity OK - tunnel issue may be temporary"
            else
                log_message "❌ Network connectivity issue detected"
            fi
            ;;
        "HTTP_ERROR")
            log_message "🔄 HTTP error detected - checking service health"
            # Check if backend service is running
            if supervisorctl status backend | grep -q "RUNNING"; then
                log_message "✅ Backend service running - checking configuration"
            else
                log_message "❌ Backend service not running - attempting restart"
                supervisorctl restart backend
            fi
            ;;
        "PERFORMANCE_DEGRADATION")
            log_message "🔄 Performance issue detected - monitoring response times"
            ;;
    esac
    
    return 0
}

run_health_check_cycle() {
    log_message "🔄 Starting tunnel health check cycle..."
    
    if validate_tunnel_system; then
        log_message "✅ All tunnel systems healthy"
        return 0
    else
        log_message "⚠️ Tunnel validation failed - investigating..."
        
        # Determine issue type and handle appropriately
        local backend_result=$(check_emergent_tunnel_health "$EMERGENT_TUNNEL_URL" "$BACKEND_HEALTH_ENDPOINT")
        local frontend_result=$(check_emergent_tunnel_health "$EMERGENT_TUNNEL_URL" "$FRONTEND_HEALTH_ENDPOINT")
        
        if [[ "$backend_result" =~ CONNECTION_ERROR || "$frontend_result" =~ CONNECTION_ERROR ]]; then
            handle_tunnel_degradation "CONNECTION_ERROR"
        elif [[ "$backend_result" =~ HTTP_ERROR || "$frontend_result" =~ HTTP_ERROR ]]; then
            handle_tunnel_degradation "HTTP_ERROR"
        else
            handle_tunnel_degradation "UNKNOWN"
        fi
        
        return 1
    fi
}

# Main monitoring loop
log_message "🚀 Emergent Tunnel Watchdog started (replacing legacy ngrok monitoring)"
log_message "📡 Monitoring tunnel: $EMERGENT_TUNNEL_URL"

consecutive_failures=0
max_failures=3
health_check_interval=60  # Check every minute (less aggressive than legacy 30s)
performance_check_interval=300  # Performance check every 5 minutes

last_performance_check=0

while true; do
    current_time=$(date +%s)
    
    # Regular health check
    if run_health_check_cycle; then
        if [ $consecutive_failures -gt 0 ]; then
            log_message "🎉 Tunnel system recovered after $consecutive_failures failure(s)"
        fi
        consecutive_failures=0
    else
        consecutive_failures=$((consecutive_failures + 1))
        log_message "⚠️ Health check failed (failure $consecutive_failures/$max_failures)"
        
        if [ $consecutive_failures -ge $max_failures ]; then
            log_message "🚨 Multiple consecutive failures detected - escalating to recovery mode"
            
            # More sophisticated recovery than legacy system
            log_message "🔄 Attempting intelligent recovery..."
            
            # Check system resources
            local memory_usage=$(free | awk 'NR==2{printf "%.2f%%", $3*100/$2}')
            local cpu_load=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs)
            
            log_message "📊 System stats: Memory: $memory_usage, CPU Load: $cpu_load"
            
            # Gentle service restart (not aggressive like legacy)
            if (( consecutive_failures >= 5 )); then
                log_message "🔄 Attempting service restart (last resort)..."
                supervisorctl restart expo
                sleep 10
            fi
            
            consecutive_failures=0
        fi
    fi
    
    # Performance monitoring (less frequent)
    if [ $((current_time - last_performance_check)) -ge $performance_check_interval ]; then
        log_message "📈 Running performance check..."
        
        local backend_result=$(check_emergent_tunnel_health "$EMERGENT_TUNNEL_URL" "$BACKEND_HEALTH_ENDPOINT")
        local backend_time=$(echo "$backend_result" | cut -d'|' -f3)
        
        if (( $(echo "$backend_time > 2.0" | bc -l 2>/dev/null || echo "0") )); then
            log_message "⚠️ Performance degradation detected: ${backend_time}s response time"
            handle_tunnel_degradation "PERFORMANCE_DEGRADATION"
        else
            log_message "✅ Performance OK: ${backend_time}s response time"
        fi
        
        last_performance_check=$current_time
    fi
    
    # Wait before next check (smarter interval than legacy)
    sleep $health_check_interval
done