#!/bin/bash
# Simple backup script for GenX FX data

BACKUP_DIR="/home/ec2-user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup application data
docker exec genx-fx tar czf - /app/data /app/logs 2>/dev/null | cat > "$BACKUP_DIR/genx-data-$DATE.tar.gz"

# Keep only last 7 backups
find $BACKUP_DIR -name "genx-data-*.tar.gz" -mtime +7 -delete

echo "Backup completed: genx-data-$DATE.tar.gz"
