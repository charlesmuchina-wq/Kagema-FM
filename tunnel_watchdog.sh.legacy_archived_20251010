#!/bin/bash
"""
Kagema FM Tunnel Watchdog
Lightweight script for immediate tunnel issue detection and resolution
"""

LOG_FILE="/var/log/tunnel_watchdog.log"
TUNNEL_MANAGER="/app/tunnel_manager.py"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_ngrok_api() {
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_tunnel_connectivity() {
    local tunnel_url=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url' 2>/dev/null | head -1)
    
    if [[ -n "$tunnel_url" ]] && [[ "$tunnel_url" != "null" ]]; then
        if curl -s --max-time 10 "$tunnel_url" > /dev/null 2>&1; then
            echo "$tunnel_url"
            return 0
        fi
    fi
    return 1
}

handle_tunnel_issue() {
    log_message "🚨 TUNNEL ISSUE DETECTED - Triggering auto-recovery"
    
    # Check for specific error patterns in logs
    if tail -20 /var/log/supervisor/expo.err.log | grep -q "ERR_NGROK"; then
        local error=$(tail -20 /var/log/supervisor/expo.err.log | grep "ERR_NGROK" | tail -1)
        log_message "📋 Detected error: $error"
    fi
    
    # Kill any stuck ngrok processes
    pkill -f ngrok 2>/dev/null
    sleep 2
    
    # Restart expo service
    log_message "🔄 Restarting Expo service..."
    supervisorctl stop expo
    sleep 3
    supervisorctl start expo
    
    # Wait for tunnel to be ready
    log_message "⏳ Waiting for tunnel to be ready..."
    local attempts=0
    local max_attempts=24  # 2 minutes with 5-second intervals
    
    while [ $attempts -lt $max_attempts ]; do
        sleep 5
        if tunnel_url=$(check_tunnel_connectivity); then
            log_message "✅ Tunnel recovered successfully: $tunnel_url"
            return 0
        fi
        attempts=$((attempts + 1))
        log_message "⏳ Still waiting... (attempt $attempts/$max_attempts)"
    done
    
    log_message "❌ Auto-recovery failed after $max_attempts attempts"
    return 1
}

# Main monitoring loop
log_message "🚀 Kagema FM Tunnel Watchdog started"

consecutive_failures=0
max_failures=3

while true; do
    # Quick health check
    if check_ngrok_api; then
        if tunnel_url=$(check_tunnel_connectivity); then
            # Success - reset failure counter
            if [ $consecutive_failures -gt 0 ]; then
                log_message "✅ Tunnel recovered: $tunnel_url"
            fi
            consecutive_failures=0
        else
            consecutive_failures=$((consecutive_failures + 1))
            log_message "⚠️ Tunnel not accessible (failure $consecutive_failures/$max_failures)"
            
            if [ $consecutive_failures -ge $max_failures ]; then
                handle_tunnel_issue
                consecutive_failures=0
            fi
        fi
    else
        consecutive_failures=$((consecutive_failures + 1))
        log_message "⚠️ Ngrok API not accessible (failure $consecutive_failures/$max_failures)"
        
        if [ $consecutive_failures -ge $max_failures ]; then
            handle_tunnel_issue
            consecutive_failures=0
        fi
    fi
    
    # Wait before next check
    sleep 30
done