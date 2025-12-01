#!/bin/bash
# Database restore script for Emily Word Tracker
# Usage: ./scripts/restore_db.sh <backup_file.sql>
#
# WARNING: This will overwrite all data in the production database!
# Requires Docker (uses postgres:17 image to match Railway's version)

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for backup file argument
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql>"
    echo ""
    echo "Available backups:"
    ls -lt backups/*.sql 2>/dev/null | head -10 || echo "  No backups found in backups/"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    echo "Install Docker or use a PostgreSQL 17 client."
    exit 1
fi

# Railway PostgreSQL connection details
PGHOST="${PGHOST:-hopper.proxy.rlwy.net}"
PGPORT="${PGPORT:-48793}"
PGDATABASE="${PGDATABASE:-railway}"
PGUSER="${PGUSER:-postgres}"
PGPASSWORD="${PGPASSWORD}"

if [ -z "$PGPASSWORD" ]; then
    echo "Error: PGPASSWORD not set. Add it to .env file or export it."
    exit 1
fi

echo "=========================================="
echo "WARNING: DATABASE RESTORE"
echo "=========================================="
echo "This will OVERWRITE all data in the production database!"
echo ""
echo "Host: $PGHOST:$PGPORT"
echo "Database: $PGDATABASE"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Starting restore..."
echo "Using Docker postgres:17 image for compatibility..."

# Get absolute path for Docker mount
BACKUP_FILE_ABS=$(realpath "$BACKUP_FILE")
BACKUP_FILE_NAME=$(basename "$BACKUP_FILE")

# Run psql via Docker (postgres:17 to match Railway)
docker run --rm \
    -e PGPASSWORD="$PGPASSWORD" \
    -v "$BACKUP_FILE_ABS:/backup/$BACKUP_FILE_NAME:ro" \
    postgres:17 \
    psql \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -U "$PGUSER" \
    -d "$PGDATABASE" \
    -f "/backup/$BACKUP_FILE_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "Restore complete!"
else
    echo "Restore failed!"
    exit 1
fi
