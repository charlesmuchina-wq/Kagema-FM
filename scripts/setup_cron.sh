#!/bin/bash

# Setup cron jobs for Dragon KARAU AI monitoring

echo "Setting up cron jobs for health monitoring..."

# Create cron job file
CRON_FILE="/tmp/dragon-karau-cron"

# Add health check every 5 minutes
echo "# Dragon KARAU AI - Health Check (every 5 minutes)" > "$CRON_FILE"
echo "*/5 * * * * /app/scripts/health_check.sh >> /var/log/dragon-karau-health.log 2>&1" >> "$CRON_FILE"

# Add configuration validation daily at 2 AM
echo "" >> "$CRON_FILE"
echo "# Configuration Validation (daily at 2 AM)" >> "$CRON_FILE"
echo "0 2 * * * /app/scripts/validate_config.sh >> /var/log/dragon-karau-validation.log 2>&1" >> "$CRON_FILE"

# Add log rotation weekly on Sunday at 3 AM
echo "" >> "$CRON_FILE"
echo "# Log Rotation (weekly on Sunday at 3 AM)" >> "$CRON_FILE"
echo "0 3 * * 0 /app/scripts/rotate_logs.sh >> /var/log/dragon-karau-maintenance.log 2>&1" >> "$CRON_FILE"

# Install cron jobs
crontab "$CRON_FILE"

# Verify installation
echo ""
echo "Installed cron jobs:"
crontab -l

echo ""
echo "✅ Cron jobs setup complete!"
echo ""
echo "Health checks will run every 5 minutes"
echo "Configuration validation will run daily at 2 AM"
echo "Log rotation will run weekly on Sunday at 3 AM"
