#!/bin/bash

# Dragon KARAU AI - Service Health Check Script
# This script monitors service health and automatically restarts failed services

LOG_FILE="/var/log/dragon-karau-health.log"
ALERT_EMAIL="alerts@dragonkarau.com"  # Configure your alert destination

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_service_status() {
    SERVICE=$1
    STATUS=$(sudo supervisorctl status "$SERVICE" 2>&1)
    
    if echo "$STATUS" | grep -q "RUNNING"; then
        log_message "✅ $SERVICE is running"
        return 0
    else
        log_message "❌ $SERVICE is NOT running: $STATUS"
        return 1
    fi
}

restart_service() {
    SERVICE=$1
    log_message "🔄 Attempting to restart $SERVICE..."
    
    sudo supervisorctl restart "$SERVICE"
    sleep 5
    
    if check_service_status "$SERVICE"; then
        log_message "✅ $SERVICE restarted successfully"
        return 0
    else
        log_message "❌ $SERVICE restart FAILED"
        return 1
    fi
}

check_frontend_health() {
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
    
    if [ "$RESPONSE" = "200" ]; then
        log_message "✅ Frontend health check passed (HTTP $RESPONSE)"
        return 0
    else
        log_message "❌ Frontend health check failed (HTTP $RESPONSE)"
        return 1
    fi
}

check_backend_health() {
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/ 2>/dev/null)
    
    if [ "$RESPONSE" = "200" ]; then
        log_message "✅ Backend health check passed (HTTP $RESPONSE)"
        return 0
    else
        log_message "❌ Backend health check failed (HTTP $RESPONSE)"
        return 1
    fi
}

send_alert() {
    MESSAGE=$1
    log_message "🚨 ALERT: $MESSAGE"
    
    # Send alert (implement your notification system)
    # Example: Send to Slack, email, PagerDuty, etc.
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"$MESSAGE\"}" \
    #   "$SLACK_WEBHOOK_URL"
}

main() {
    log_message "========================================="
    log_message "Starting health check cycle"
    log_message "========================================="
    
    # Check critical services
    SERVICES=("expo" "backend" "mongodb")
    FAILED_SERVICES=()
    
    for SERVICE in "${SERVICES[@]}"; do
        if ! check_service_status "$SERVICE"; then
            FAILED_SERVICES+=("$SERVICE")
            
            # Attempt automatic restart
            if restart_service "$SERVICE"; then
                send_alert "Service $SERVICE was down but has been automatically restarted"
            else
                send_alert "CRITICAL: Service $SERVICE is down and auto-restart failed!"
            fi
        fi
    done
    
    # Wait for services to stabilize
    if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
        log_message "⏳ Waiting 15 seconds for services to stabilize..."
        sleep 15
    fi
    
    # Check HTTP endpoints
    if ! check_frontend_health; then
        log_message "⚠️ Frontend not responding, attempting restart..."
        restart_service "expo"
        sleep 10
        
        if ! check_frontend_health; then
            send_alert "CRITICAL: Frontend still not responding after restart!"
        fi
    fi
    
    if ! check_backend_health; then
        log_message "⚠️ Backend not responding, attempting restart..."
        restart_service "backend"
        sleep 10
        
        if ! check_backend_health; then
            send_alert "CRITICAL: Backend still not responding after restart!"
        fi
    fi
    
    log_message "========================================="
    log_message "Health check cycle complete"
    log_message "========================================="
    echo ""
}

# Run the health check
main
