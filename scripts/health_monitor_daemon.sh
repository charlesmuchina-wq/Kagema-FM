#!/bin/bash

# Health Monitor Daemon - Runs continuously in background
# Alternative to cron for container environments

LOG_FILE="/var/log/dragon-karau-health.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Health Monitor Daemon started" >> "$LOG_FILE"

while true; do
    # Run health check every 5 minutes (300 seconds)
    /app/scripts/health_check.sh >> "$LOG_FILE" 2>&1
    
    # Sleep for 5 minutes
    sleep 300
done
