#!/bin/bash
# Database backup script for Emily Word Tracker
# Usage: ./scripts/backup_db.sh
#
# Requires Docker (uses postgres:17 image to match Railway's version)

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
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

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    echo "Install Docker or use a PostgreSQL 17 client."
    exit 1
fi

# Create backups directory if it doesn't exist
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/emily_words_${TIMESTAMP}.sql"

echo "Starting backup of Railway PostgreSQL database..."
echo "Host: $PGHOST:$PGPORT"
echo "Database: $PGDATABASE"
echo "Using Docker postgres:17 image for compatibility..."

# Run pg_dump via Docker (postgres:17 to match Railway)
docker run --rm \
    -e PGPASSWORD="$PGPASSWORD" \
    postgres:17 \
    pg_dump \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -U "$PGUSER" \
    -d "$PGDATABASE" \
    -F p \
    --no-owner \
    --no-acl \
    > "$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    echo "Backup successful: $BACKUP_FILE"
    echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"

    # Keep only last 10 backups
    cd "$BACKUP_DIR"
    ls -t emily_words_*.sql 2>/dev/null | tail -n +11 | xargs -r rm --
    cd ..

    echo "Backup complete!"
else
    echo "Backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi
