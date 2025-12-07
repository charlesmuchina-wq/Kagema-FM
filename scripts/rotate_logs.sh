#!/bin/bash

# Log Rotation Script for Dragon KARAU AI
# Rotates logs to prevent disk space issues

LOG_DIR="/var/log"
BACKUP_DIR="/var/log/archive"
MAX_AGE_DAYS=30

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting log rotation..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Rotate Dragon KARAU logs
LOGS_TO_ROTATE=(
    "dragon-karau-health.log"
    "dragon-karau-validation.log"
    "dragon-karau-maintenance.log"
)

for LOG_FILE in "${LOGS_TO_ROTATE[@]}"; do
    LOG_PATH="$LOG_DIR/$LOG_FILE"
    
    if [ -f "$LOG_PATH" ]; then
        # Get file size
        SIZE=$(du -h "$LOG_PATH" | cut -f1)
        
        # Archive if file exists and is not empty
        if [ -s "$LOG_PATH" ]; then
            ARCHIVE_NAME="${LOG_FILE}.$(date +%Y%m%d-%H%M%S).gz"
            
            echo "Archiving $LOG_FILE ($SIZE) to $ARCHIVE_NAME"
            gzip -c "$LOG_PATH" > "$BACKUP_DIR/$ARCHIVE_NAME"
            
            # Clear the log file
            > "$LOG_PATH"
            
            echo "✅ Archived and cleared $LOG_FILE"
        else
            echo "⚠️ $LOG_FILE is empty, skipping"
        fi
    else
        echo "⚠️ $LOG_FILE not found, skipping"
    fi
done

# Clean up old archives (older than MAX_AGE_DAYS)
echo ""
echo "Cleaning up archives older than $MAX_AGE_DAYS days..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$MAX_AGE_DAYS -delete
DELETED=$(find "$BACKUP_DIR" -name "*.gz" -mtime +$MAX_AGE_DAYS 2>/dev/null | wc -l)
echo "Deleted $DELETED old archive(s)"

# Show current disk usage
echo ""
echo "Current disk usage:"
df -h / | grep -v Filesystem

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log rotation complete!"
