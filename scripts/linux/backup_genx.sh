#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/genx_backup_$DATE"
mkdir -p "$BACKUP_DIR"

# Backup important files
cp -r signal_output "$BACKUP_DIR/"
cp -r logs "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || true
cp amp_config.json "$BACKUP_DIR/" 2>/dev/null || true

# Create archive
tar -czf "backups/genx_backup_$DATE.tar.gz" -C backups "genx_backup_$DATE"
rm -rf "$BACKUP_DIR"

echo "Backup created: genx_backup_$DATE.tar.gz"

# Keep only last 7 backups
cd backups
ls -t genx_backup_*.tar.gz | tail -n +8 | xargs -r rm --
