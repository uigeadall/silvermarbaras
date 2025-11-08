#!/bin/bash
# Database backup script for Marbaras
# Usage: ./backup_db.sh

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="${MYSQL_DATABASE:-silvershop}"
DB_USER="${MYSQL_USER:-root}"
DB_PASSWORD="${MYSQL_PASSWORD}"
DB_HOST="${MYSQL_HOST:-localhost}"
DB_PORT="${MYSQL_PORT:-3306}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup filename
BACKUP_FILE="$BACKUP_DIR/marbaras_${DATE}.sql"

# Perform backup
echo "Creating backup: $BACKUP_FILE"
mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
if [ -f "$BACKUP_FILE" ]; then
    gzip "$BACKUP_FILE"
    echo "Backup compressed: ${BACKUP_FILE}.gz"
    
    # Remove backups older than 7 days
    find "$BACKUP_DIR" -name "marbaras_*.sql.gz" -mtime +7 -delete
    echo "Old backups cleaned up"
else
    echo "Error: Backup failed!"
    exit 1
fi

echo "Backup completed successfully!"

